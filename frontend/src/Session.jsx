import React, { useEffect, useRef, useState, useCallback } from 'react'
import axios from 'axios'
import * as faceapi from 'face-api.js'
import { FaceMesh } from '@mediapipe/face_mesh'

const API = 'http://localhost:8000'

// MediaPipe FaceMesh eye landmark indices (468-point mesh)
const LEFT_EYE = [33, 160, 158, 133, 153, 144]
const RIGHT_EYE = [362, 385, 387, 263, 373, 380]
const EAR_CLOSE_THRESH = 0.21
const EAR_OPEN_THRESH = 0.25

function euclidean(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y)
}

function computeEAR(lm, indices) {
  const [p1, p2, p3, p4, p5, p6] = indices.map(i => lm[i])
  return (euclidean(p2, p6) + euclidean(p3, p5)) / (2 * euclidean(p1, p4))
}

function ema(prev, next, alpha = 0.3) {
  if (!prev) return next
  const out = {}
  for (const k of Object.keys(next)) {
    out[k] = alpha * (next[k] ?? 0) + (1 - alpha) * (prev[k] ?? 0)
  }
  return out
}

const LIKERT_OPTIONS = [
  { value: 1, label: 'Strongly Disagree', short: 'SD', color: 'bg-emerald-500' },
  { value: 2, label: 'Disagree', short: 'D', color: 'bg-emerald-400' },
  { value: 3, label: 'Neutral', short: 'N', color: 'bg-slate-400' },
  { value: 4, label: 'Agree', short: 'A', color: 'bg-rose-400' },
  { value: 5, label: 'Strongly Agree', short: 'SA', color: 'bg-rose-500' },
]

const EMOTION_COLORS = {
  happy: 'text-emerald-400', neutral: 'text-sky-400', surprised: 'text-yellow-400',
  sad: 'text-blue-400', angry: 'text-red-400', fearful: 'text-orange-400', disgusted: 'text-purple-400',
}

export default function Session({ ageGroup, onSessionEnd }) {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)
  const faceMeshRef = useRef(null)
  const animFrameRef = useRef(null)
  const emotionTimerRef = useRef(null)
  const sessionStartRef = useRef(null)

  // Blink tracking refs
  const blinkCountRef = useRef(0)
  const earBelowRef = useRef(false)
  const blinkTimestampsRef = useRef([])

  // Emotion tracking
  const emotionHistoryRef = useRef(null)
  const faceApiReadyRef = useRef(false)

  // ── State ──────────────────────────────────────────────────────────────────
  const [questions, setQuestions] = useState([])
  const [currentIdx, setCurrentIdx] = useState(0)
  const [answers, setAnswers] = useState([])
  const [selectedValue, setSelectedValue] = useState(null)
  const [cameraError, setCameraError] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)

  // Live CV stats
  const [blinkCount, setBlinkCount] = useState(0)
  const [blinkBPM, setBlinkBPM] = useState(0)
  const [dominantEmotion, setDominantEmotion] = useState('—')
  const [emotionConf, setEmotionConf] = useState(0)
  const [cvStatus, setCvStatus] = useState('Loading models…')

  const visionRef = useRef({
    blink_count: 0,
    blink_rate_bpm: 0,
    session_duration_s: 0,
    emotion_distribution: null,
    dominant_emotion: null,
  })

  // ── Camera ─────────────────────────────────────────────────────────────────
  useEffect(() => {
    let mounted = true
    navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } })
      .then(stream => {
        if (!mounted) { stream.getTracks().forEach(t => t.stop()); return }
        streamRef.current = stream
        if (videoRef.current) {
          videoRef.current.srcObject = stream
          videoRef.current.play().catch(() => { })
        }
        sessionStartRef.current = Date.now()
      })
      .catch(() => { if (mounted) setCameraError(true) })
    return () => {
      mounted = false
      streamRef.current?.getTracks().forEach(t => t.stop())
    }
  }, [])

  // ── Load face-api.js models ────────────────────────────────────────────────
  useEffect(() => {
    faceapi.nets.tinyFaceDetector.loadFromUri('/models')
      .then(() => faceapi.nets.faceExpressionNet.loadFromUri('/models'))
      .then(() => { faceApiReadyRef.current = true })
      .catch(e => console.warn('[face-api] model load failed:', e))
  }, [])

  // ── MediaPipe FaceMesh ─────────────────────────────────────────────────────
  useEffect(() => {
    const mesh = new FaceMesh({
      locateFile: f => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh@0.4/${f}`,
    })
    mesh.setOptions({
      maxNumFaces: 1,
      refineLandmarks: false,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5,
    })
    mesh.onResults(onFaceMeshResults)
    faceMeshRef.current = mesh

    mesh.initialize().then(() => {
      setCvStatus('CV active')
      startRenderLoop()
    }).catch(e => {
      console.warn('[FaceMesh] init failed:', e)
      setCvStatus('CV unavailable')
    })

    return () => {
      cancelAnimationFrame(animFrameRef.current)
      clearInterval(emotionTimerRef.current)
      mesh.close?.()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function startRenderLoop() {
    const loop = async () => {
      if (videoRef.current && videoRef.current.readyState >= 2 && faceMeshRef.current) {
        await faceMeshRef.current.send({ image: videoRef.current })
      }
      animFrameRef.current = requestAnimationFrame(loop)
    }
    animFrameRef.current = requestAnimationFrame(loop)
    emotionTimerRef.current = setInterval(runEmotionDetection, 500)
  }

  function onFaceMeshResults(results) {
    if (!results.multiFaceLandmarks?.length) return
    const lm = results.multiFaceLandmarks[0]
    const earL = computeEAR(lm, LEFT_EYE)
    const earR = computeEAR(lm, RIGHT_EYE)
    const ear = (earL + earR) / 2

    if (ear < EAR_CLOSE_THRESH && !earBelowRef.current) {
      earBelowRef.current = true
    } else if (ear > EAR_OPEN_THRESH && earBelowRef.current) {
      earBelowRef.current = false
      blinkCountRef.current += 1
      blinkTimestampsRef.current.push(Date.now())
      const cutoff = Date.now() - 60_000
      blinkTimestampsRef.current = blinkTimestampsRef.current.filter(t => t > cutoff)
      const bpm = blinkTimestampsRef.current.length
      setBlinkCount(blinkCountRef.current)
      setBlinkBPM(bpm)
      visionRef.current.blink_count = blinkCountRef.current
      visionRef.current.blink_rate_bpm = bpm
    }
  }

  async function runEmotionDetection() {
    if (!faceApiReadyRef.current || !videoRef.current) return
    if (videoRef.current.readyState < 2) return
    try {
      const detection = await faceapi
        .detectSingleFace(videoRef.current, new faceapi.TinyFaceDetectorOptions())
        .withFaceExpressions()
      if (!detection) return
      const raw = detection.expressions
      const smoothed = ema(emotionHistoryRef.current, raw, 0.3)
      emotionHistoryRef.current = smoothed
      const dom = Object.entries(smoothed).reduce((a, b) => b[1] > a[1] ? b : a)
      setDominantEmotion(dom[0])
      setEmotionConf(Math.round(dom[1] * 100))
      visionRef.current.emotion_distribution = { ...smoothed }
      visionRef.current.dominant_emotion = dom[0]
    } catch (_) { }
  }

  // ── Questions ──────────────────────────────────────────────────────────────
  useEffect(() => {
    const token = localStorage.getItem('token')
    axios
      .get(`${API}/questionnaire/questions?age_group=${encodeURIComponent(ageGroup)}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then(res => {
        setQuestions(res.data.questions)
        setAnswers(new Array(res.data.count).fill(0))
      })
      .catch(() => {
        setQuestions([{ question: 'I feel stressed in my daily life', type: 'negative', category: 'emotional' }])
        setAnswers([0])
      })
  }, [ageGroup])

  useEffect(() => () => {
    streamRef.current?.getTracks().forEach(t => t.stop())
    cancelAnimationFrame(animFrameRef.current)
    clearInterval(emotionTimerRef.current)
  }, [])

  // ── Submit answer ──────────────────────────────────────────────────────────
  const submitAnswer = useCallback(() => {
    if (selectedValue === null) return
    const updated = [...answers]
    updated[currentIdx] = selectedValue
    setAnswers(updated)
    setSelectedValue(null)

    if (currentIdx + 1 >= questions.length) {
      finishSession(updated)
    } else {
      setCurrentIdx(i => i + 1)
    }
  }, [selectedValue, answers, currentIdx, questions])

  const goBack = useCallback(() => {
    if (currentIdx > 0) {
      setCurrentIdx(i => i - 1)
      setSelectedValue(answers[currentIdx - 1] || null)
    }
  }, [currentIdx, answers])

  const finishSession = async (allAnswers) => {
    setIsProcessing(true)
    cancelAnimationFrame(animFrameRef.current)
    clearInterval(emotionTimerRef.current)

    const dur = sessionStartRef.current
      ? (Date.now() - sessionStartRef.current) / 1000
      : 0
    visionRef.current.session_duration_s = Math.round(dur)

    const token = localStorage.getItem('token')
    try {
      const res = await axios.post(
        `${API}/session/process`,
        { age_group: ageGroup, visual_data: visionRef.current, answers: allAnswers },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      onSessionEnd(res.data)
    } catch {
      onSessionEnd({
        risk_score: 35, risk_level: 'Mild',
        recommendation: 'Could not process results. Please try again.',
        questionnaire: { score: 0, level: 'Unknown', categories: {} },
        visual_summary: { avg_blink_rate: 0, dominant_emotion: 'unknown', emotion_distribution: {} },
      })
    }
  }

  // ── Derived ────────────────────────────────────────────────────────────────
  const progressPct = questions.length > 0 ? Math.round(((currentIdx) / questions.length) * 100) : 0
  const isLastQuestion = currentIdx + 1 >= questions.length
  const currentQ = questions[currentIdx] || {}
  const emotionColor = EMOTION_COLORS[dominantEmotion] || 'text-slate-400'

  const CATEGORY_ICONS = {
    emotional: '💭', social: '👥', sleep: '😴', school: '📚',
    focus: '🎯', future: '🔮', interest: '🎨', work: '💼',
    financial: '💰', motivation: '🚀', general: '📊',
  }

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen grid lg:grid-cols-5 gap-0 relative">

      {/* ════ LEFT — CAMERA ════ */}
      <div className="lg:col-span-2 relative bg-slate-950 flex flex-col items-center justify-center p-6 min-h-[300px]">
        <div className="relative w-full max-w-sm rounded-2xl overflow-hidden shadow-2xl border border-slate-800 aspect-video bg-slate-900">
          <video ref={videoRef} autoPlay muted playsInline
            className="w-full h-full object-cover scale-x-[-1]" />
          <canvas ref={canvasRef} className="hidden" />

          {cameraError && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 text-slate-400 bg-slate-900/90">
              <svg className="w-10 h-10 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M15 10l4.553-2.069A1 1 0 0121 8.817v6.366a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <span className="text-xs text-center px-4">Camera unavailable<br />Session continues without video</span>
            </div>
          )}

          {!cameraError && (
            <div className="absolute top-3 left-3 flex items-center gap-1.5 bg-black/60 backdrop-blur px-2.5 py-1 rounded-full border border-red-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
              <span className="text-[10px] font-bold uppercase tracking-wider text-red-400">Live</span>
            </div>
          )}

          <div className="absolute top-3 right-3 bg-black/60 backdrop-blur px-2 py-1 rounded-full">
            <span className="text-[9px] font-mono text-slate-400">{cvStatus}</span>
          </div>
        </div>

        {/* Live CV Stats */}
        <div className="mt-4 grid grid-cols-3 gap-2 w-full max-w-sm">
          <div className="glass rounded-lg p-2 text-center">
            <div className="text-xs font-bold text-sky-400">{blinkCount}</div>
            <div className="text-[10px] text-slate-500 mt-0.5">Blinks</div>
          </div>
          <div className="glass rounded-lg p-2 text-center">
            <div className="text-xs font-bold text-emerald-400">{blinkBPM}/min</div>
            <div className="text-[10px] text-slate-500 mt-0.5">Blink Rate</div>
          </div>
          <div className="glass rounded-lg p-2 text-center">
            <div className={`text-xs font-bold capitalize ${emotionColor}`}>
              {dominantEmotion === '—' ? '—' : `${dominantEmotion} ${emotionConf}%`}
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">Emotion</div>
          </div>
        </div>

        {/* Info */}
        <p className="text-[10px] text-slate-600 mt-3 text-center max-w-sm">
          Camera analyzes facial expressions &amp; blink patterns in real-time while you answer the questionnaire.
        </p>
      </div>

      {/* ════ RIGHT — QUESTIONNAIRE ════ */}
      <div className="lg:col-span-3 flex flex-col justify-center p-8 bg-slate-900/50">

        {/* Progress */}
        <div className="mb-6">
          <div className="flex justify-between text-xs text-slate-500 mb-2">
            <span>Assessment Progress</span>
            <span>{currentIdx + (selectedValue ? 1 : 0)} / {questions.length} answered</span>
          </div>
          <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-sky-500 to-violet-500 transition-all duration-700"
              style={{ width: `${progressPct}%` }} />
          </div>
        </div>

        {/* Question card */}
        <div className="glass rounded-2xl p-7 mb-5 border border-slate-700/50 min-h-[160px] flex flex-col justify-center">
          {questions.length > 0 ? (
            <>
              <div className="flex items-center gap-3 mb-4">
                <span className="text-2xl">{CATEGORY_ICONS[currentQ.category] || '📋'}</span>
                <div>
                  <span className="text-xs font-bold uppercase tracking-widest text-sky-400">
                    Question {currentIdx + 1} of {questions.length}
                  </span>
                  <span className="ml-3 text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 capitalize">
                    {currentQ.category}
                  </span>
                </div>
              </div>
              <p className="text-xl font-semibold text-white leading-relaxed">
                {currentQ.question}
              </p>
            </>
          ) : (
            <div className="text-center text-slate-500">
              <svg className="w-8 h-8 mx-auto mb-2 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Loading questions...
            </div>
          )}
        </div>

        {/* Likert Scale */}
        {questions.length > 0 && (
          <div className="mb-6">
            <p className="text-xs text-slate-500 mb-3 text-center">How much do you agree with this statement?</p>
            <div className="grid grid-cols-5 gap-2">
              {LIKERT_OPTIONS.map(opt => (
                <button
                  key={opt.value}
                  onClick={() => setSelectedValue(opt.value)}
                  className={`group relative flex flex-col items-center gap-1.5 py-4 px-2 rounded-xl border-2 transition-all duration-200
                    ${selectedValue === opt.value
                      ? `${opt.color} border-white/40 text-white shadow-lg scale-105`
                      : 'bg-slate-800/50 border-slate-700/50 text-slate-400 hover:border-slate-500 hover:bg-slate-800'
                    }`}
                >
                  <span className={`text-lg font-black ${selectedValue === opt.value ? 'text-white' : 'text-slate-300'}`}>
                    {opt.value}
                  </span>
                  <span className={`text-[10px] font-medium text-center leading-tight ${selectedValue === opt.value ? 'text-white/90' : 'text-slate-500'}`}>
                    {opt.label}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Controls */}
        <div className="flex items-center gap-3">
          <button
            onClick={goBack}
            disabled={currentIdx === 0}
            className="text-slate-500 hover:text-white disabled:opacity-20 disabled:cursor-not-allowed
                       transition-colors py-3 px-5 rounded-xl text-sm font-medium hover:bg-slate-800"
          >
            ← Back
          </button>

          <div className="flex-1" />

          <button
            id="next-question-btn"
            onClick={submitAnswer}
            disabled={selectedValue === null}
            className="bg-sky-500 hover:bg-sky-400 disabled:opacity-30 disabled:cursor-not-allowed
                       text-slate-900 font-bold py-3 px-7 rounded-xl transition-all active:scale-95 text-sm whitespace-nowrap"
          >
            {isLastQuestion ? '✓ Finish Assessment' : 'Next →'}
          </button>
        </div>

        <p className="text-xs text-slate-600 mt-5 text-center">
          Age Group: <span className="text-slate-500">{ageGroup}</span>
          &nbsp;·&nbsp; Select an option then click Next
        </p>
      </div>

      {/* Processing overlay */}
      {isProcessing && (
        <div className="fixed inset-0 bg-slate-950/95 backdrop-blur z-50 flex flex-col items-center justify-center gap-6">
          <div className="relative">
            <div className="w-20 h-20 rounded-full border-4 border-sky-500/20" />
            <div className="w-20 h-20 rounded-full border-4 border-sky-500 border-t-transparent animate-spin absolute inset-0" />
          </div>
          <div className="text-center">
            <h2 className="text-2xl font-bold text-white mb-2">Analyzing Results</h2>
            <p className="text-slate-400 text-sm">Combining questionnaire, facial emotion &amp; blink analysis…</p>
          </div>
        </div>
      )}
    </div>
  )
}
