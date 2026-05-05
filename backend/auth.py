import random
import smtplib
import logging
from datetime import datetime, timedelta
from typing import Dict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jose import JWTError, jwt
from fastapi import HTTPException
from config import settings

logger = logging.getLogger("auth")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

# In-memory storage for OTPs (In production, use Redis)
otp_store: Dict[str, Dict] = {}


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


def send_otp_email(email: str, otp: str) -> bool:
    """
    Send OTP via Gmail SMTP with App Password.
    Returns True on success, False on failure (never raises).
    All errors are logged with full detail for debugging.
    """
    smtp_user = settings.SMTP_USERNAME
    smtp_pass = settings.SMTP_PASSWORD
    smtp_host = settings.SMTP_SERVER
    smtp_port = settings.SMTP_PORT

    # ── Pre-flight checks ─────────────────────────────────────────────────
    if not smtp_user or smtp_user == "your-email@gmail.com":
        logger.error("SMTP_USERNAME is not configured in .env — email cannot be sent")
        return False

    if not smtp_pass or smtp_pass == "your-app-password":
        logger.error("SMTP_PASSWORD is not configured in .env — email cannot be sent")
        return False

    logger.info(f"Attempting to send OTP to {email} via {smtp_host}:{smtp_port}")
    logger.info(f"Sender: {smtp_user}")

    # ── Build the email ───────────────────────────────────────────────────
    msg = MIMEMultipart("alternative")
    msg["From"] = f"BehavioralSense <{smtp_user}>"
    msg["To"] = email
    msg["Subject"] = "BehavioralSense - Your Login OTP"

    html_body = f"""\
<html>
  <body style="font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 30px;">
    <div style="max-width: 480px; margin: 0 auto; background: #1e293b; border-radius: 16px; padding: 32px; border: 1px solid #334155;">
      <h2 style="color: #38bdf8; margin-top: 0;">BehavioralSense</h2>
      <p>Hello,</p>
      <p>Your one-time login code is:</p>
      <div style="text-align: center; margin: 24px 0;">
        <span style="font-size: 36px; font-weight: bold; color: #38bdf8; letter-spacing: 8px; font-family: monospace;">{otp}</span>
      </div>
      <p>This code expires in <strong>{settings.OTP_EXPIRE_MINUTES} minutes</strong>.</p>
      <p style="color: #94a3b8; font-size: 13px; margin-top: 24px;">If you did not request this code, please ignore this email.</p>
    </div>
  </body>
</html>"""

    plain_body = f"Your BehavioralSense OTP is: {otp}\nExpires in {settings.OTP_EXPIRE_MINUTES} minutes."

    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    # ── Send via SMTP ─────────────────────────────────────────────────────
    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
        server.set_debuglevel(0)  # Set to 1 for full SMTP debug output
        server.ehlo()

        logger.info("SMTP connection established — starting TLS...")
        server.starttls()
        server.ehlo()

        logger.info("TLS active — authenticating...")
        server.login(smtp_user, smtp_pass)
        logger.info("SMTP authentication successful")

        server.send_message(msg)
        server.quit()

        logger.info(f"✅ OTP email sent successfully to {email}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ SMTP AUTH FAILED: {e}")
        logger.error(
            "FIX: Go to https://myaccount.google.com/apppasswords\n"
            "     1. Enable 2-Step Verification on your Google account\n"
            "     2. Generate an App Password for 'Mail'\n"
            "     3. Put the 16-character password in backend/.env as SMTP_PASSWORD"
        )
        return False

    except smtplib.SMTPConnectError as e:
        logger.error(f"❌ SMTP CONNECTION FAILED: {e}")
        logger.error("FIX: Check your internet connection and firewall settings")
        return False

    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"❌ RECIPIENT REFUSED: {e}")
        logger.error("FIX: The recipient email address may be invalid")
        return False

    except smtplib.SMTPException as e:
        logger.error(f"❌ SMTP ERROR: {type(e).__name__}: {e}")
        return False

    except TimeoutError:
        logger.error("❌ SMTP TIMEOUT: Connection to Gmail timed out after 15 seconds")
        logger.error("FIX: Check internet / firewall — port 587 may be blocked")
        return False

    except Exception as e:
        logger.error(f"❌ UNEXPECTED EMAIL ERROR: {type(e).__name__}: {e}")
        return False


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
