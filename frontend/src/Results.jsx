import React from 'react'

const RISK_CONFIG = {
  Low:      { color: 'text-emerald-400', bg: 'bg-emerald-400/10', border: 'border-emerald-400/30', emoji: '✅', bar: 'bg-emerald-400' },
  Mild:     { color: 'text-sky-400',     bg: 'bg-sky-400/10',     border: 'border-sky-400/30',     emoji: '💙', bar: 'bg-sky-400' },
  Moderate: { color: 'text-amber-400',   bg: 'bg-amber-400/10',   border: 'border-amber-400/30',   emoji: '⚠️', bar: 'bg-amber-400' },
  Elevated: { color: 'text-rose-400',    bg: 'bg-rose-400/10',    border: 'border-rose-400/30',     emoji: '🚨', bar: 'bg-rose-400' },
}

const CATEGORY_ICONS = {
  emotional: '💭', social: '👥', sleep: '😴', school: '📚',
  focus: '🎯', future: '🔮', interest: '🎨', work: '💼',
  financial: '💰', motivation: '🚀', general: '📊',
}

const EMOTION_COLORS = {
  happy: 'bg-emerald-400', neutral: 'bg-sky-400', surprised: 'bg-yellow-400',
  sad: 'bg-blue-400', angry: 'bg-red-400', fearful: 'bg-orange-400', disgusted: 'bg-purple-400',
}

function ScoreBar({ label, value, color = 'bg-sky-400', detail = '' }) {
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between items-baseline">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-500">{label}</span>
        <span className="text-sm font-black text-white">{Math.round(value)}%</span>
      </div>
      <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all duration-1000`}
          style={{ width: `${Math.min(100, value)}%` }} />
      </div>
      {detail && <p className="text-[11px] text-slate-600">{detail}</p>}
    </div>
  )
}

function CategoryBreakdown({ categories }) {
  if (!categories || !Object.keys(categories).length) return null
  const sorted = Object.entries(categories).sort((a, b) => b[1].percentage - a[1].percentage)

  return (
    <div className="space-y-3">
      {sorted.map(([key, cat]) => {
        const pct = cat.percentage
        const barColor = pct >= 60 ? 'bg-rose-400' : pct >= 30 ? 'bg-amber-400' : 'bg-emerald-400'
        return (
          <div key={key}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-slate-300 flex items-center gap-1.5">
                <span>{CATEGORY_ICONS[key] || '📋'}</span>
                {cat.label}
              </span>
              <span className={`text-xs font-bold ${pct >= 60 ? 'text-rose-400' : pct >= 30 ? 'text-amber-400' : 'text-emerald-400'}`}>
                {pct}%
              </span>
            </div>
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
              <div className={`h-full ${barColor} rounded-full transition-all duration-1000`}
                style={{ width: `${pct}%` }} />
            </div>
          </div>
        )
      })}
    </div>
  )
}

function EmotionDistChart({ dist }) {
  if (!dist || !Object.keys(dist).length) return null
  const sorted = Object.entries(dist).sort((a, b) => b[1] - a[1])
  return (
    <div className="space-y-2 mt-3">
      {sorted.map(([em, conf]) => (
        <div key={em} className="flex items-center gap-2">
          <span className="text-[11px] text-slate-400 w-20 capitalize">{em}</span>
          <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div className={`h-full ${EMOTION_COLORS[em] || 'bg-slate-500'} rounded-full`}
              style={{ width: `${Math.round(conf * 100)}%` }} />
          </div>
          <span className="text-[11px] text-slate-500 w-10 text-right">{Math.round(conf * 100)}%</span>
        </div>
      ))}
    </div>
  )
}

export default function Results({ results, onReset }) {
  const cfg = RISK_CONFIG[results.risk_level] || RISK_CONFIG['Mild']
  const vs = results.visual_summary || {}
  const bd = results.score_breakdown || {}
  const q = results.questionnaire || {}

  return (
    <div className="min-h-screen py-12 px-4 max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center mb-10">
        <div className="inline-flex items-center gap-2 text-slate-400 text-sm mb-4">
          <span>🧠</span><span>BehavioralSense · Assessment Complete</span>
        </div>
        <h1 className="text-4xl font-black gradient-text mb-2">Your Results</h1>
        <p className="text-slate-400 text-sm">Multi-modal stress screening summary</p>
      </div>

      {/* Risk Banner */}
      <div className={`glass rounded-3xl p-8 mb-6 border-2 ${cfg.border} ${cfg.bg} flex flex-col items-center text-center`}>
        <div className="text-5xl mb-4">{cfg.emoji}</div>
        <p className="text-slate-400 text-sm uppercase tracking-widest mb-2">Overall Stress Level</p>
        <h2 className={`text-6xl font-black mb-4 ${cfg.color}`}>{results.risk_level}</h2>
        <div className="h-2 w-48 rounded-full bg-slate-800 mb-6 overflow-hidden">
          <div className={`h-full ${cfg.bar} transition-all duration-1000`}
            style={{ width: `${results.risk_score}%` }} />
        </div>
        <p className="text-slate-200 text-lg max-w-xl leading-relaxed">{results.recommendation}</p>
      </div>

      {/* Score Breakdown (3 signals) */}
      <div className="glass rounded-2xl p-6 mb-6 border border-slate-700/50 space-y-5">
        <h3 className="font-bold text-white flex items-center gap-2">
          <span className="text-sky-400">📊</span> Score Breakdown
          <span className="ml-auto text-xs text-slate-500 font-normal">
            Questionnaire 40% · Emotion 30% · Blink 30%
          </span>
        </h3>
        <ScoreBar
          label="Psychological Questionnaire"
          value={bd.questionnaire_score ?? q.score ?? 50}
          color="bg-sky-400"
          detail={`${q.level || '—'} stress · ${q.total ?? 0}/${q.max ?? 0} points`}
        />
        <ScoreBar
          label="Facial Emotion Stress"
          value={bd.emotion_stress_score ?? 50}
          color="bg-violet-400"
          detail={`Dominant expression: ${vs.dominant_emotion || '—'}`}
        />
        <ScoreBar
          label="Blink Pattern Anomaly"
          value={bd.blink_anomaly_score ?? 50}
          color="bg-emerald-400"
          detail={`Blink rate: ${vs.avg_blink_rate ?? 0} BPM · Status: ${vs.blink_status || '—'}`}
        />
      </div>

      {/* Questionnaire Category Breakdown */}
      {q.categories && Object.keys(q.categories).length > 0 && (
        <div className="glass rounded-2xl p-6 mb-6 border border-slate-700/50">
          <h3 className="font-bold text-white mb-4 flex items-center gap-2">
            <span className="text-amber-400">📋</span> Category-wise Analysis
          </h3>
          <CategoryBreakdown categories={q.categories} />
        </div>
      )}

      {/* Visual Summary */}
      <div className="glass rounded-2xl p-6 mb-6 border border-slate-700/50">
        <h3 className="font-bold text-white mb-4 flex items-center gap-2">
          <span className="text-sky-400">👁</span> Visual Analysis (MediaPipe + face-api.js)
        </h3>
        <div className="grid grid-cols-3 gap-4 text-center mb-4">
          <div>
            <p className="text-2xl font-bold text-white">{vs.avg_blink_rate ?? 0}</p>
            <p className="text-xs text-slate-500 mt-1">Blinks/min (real EAR)</p>
          </div>
          <div>
            <p className={`text-2xl font-bold capitalize ${EMOTION_COLORS[vs.dominant_emotion]?.replace('bg-', 'text-') || 'text-slate-400'}`}>
              {vs.dominant_emotion || '—'}
            </p>
            <p className="text-xs text-slate-500 mt-1">Dominant Emotion</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{Math.round(results.risk_score)}</p>
            <p className="text-xs text-slate-500 mt-1">Overall Risk Score</p>
          </div>
        </div>
        {vs.emotion_distribution && Object.keys(vs.emotion_distribution).length > 0 && (
          <>
            <p className="text-xs font-bold uppercase text-slate-500 mb-1">Emotion Distribution</p>
            <EmotionDistChart dist={vs.emotion_distribution} />
          </>
        )}
      </div>

      {/* Explanation */}
      {results.explanation && (
        <div className="glass rounded-2xl p-6 mb-6 border border-slate-700/50">
          <h3 className="font-bold text-white mb-3 flex items-center gap-2">
            <span className="text-amber-400">💡</span> Why this score?
          </h3>
          <div className="space-y-2">
            {results.explanation.split('\n').filter(Boolean).map((line, i) => (
              <p key={i} className="text-sm text-slate-300 leading-relaxed">{line}</p>
            ))}
          </div>
        </div>
      )}

      {/* Disclaimer */}
      <div className="bg-amber-500/5 border border-amber-500/20 p-5 rounded-2xl flex gap-4 items-start mb-8">
        <span className="text-2xl flex-shrink-0">⚠️</span>
        <div>
          <p className="font-bold text-amber-400 text-sm mb-1">Important Disclaimer</p>
          <p className="text-amber-200/70 text-xs leading-relaxed">
            BehavioralSense is an early <strong>behavioural screening tool</strong> and does not provide a clinical diagnosis.
            Results are indicative only. If you are in distress, please contact a licensed mental health professional.
          </p>
        </div>
      </div>

      {/* Action */}
      <div className="text-center">
        <button id="restart-btn" onClick={onReset}
          className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm py-2 px-4 rounded-xl hover:bg-slate-800">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Start New Assessment
        </button>
      </div>
    </div>
  )
}
