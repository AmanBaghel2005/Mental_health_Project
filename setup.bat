@echo off
echo Installing backend requirements...
cd backend
pip install -r requirements.txt

echo Installing frontend dependencies...
cd ../frontend
npm install

echo Setup complete!
pause