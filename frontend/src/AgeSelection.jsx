import React from 'react'

const AGE_GROUPS = [
  {
    id: 'Child',
    emoji: '🧒',
    label: 'Child (8–12)',
    desc: 'Age-appropriate questions for younger children',
    gradient: 'from-violet-500/20 to-purple-500/10',
    border: 'border-violet-500/20 hover:border-violet-400/60',
    badge: 'bg-violet-500/20 text-violet-300',
    questions: '10 questions',
  },
  {
    id: 'Youth',
    emoji: '🧑',
    label: 'Youth (13–25)',
    desc: 'Covers academics, social life, future anxiety & emotions',
    gradient: 'from-sky-500/20 to-cyan-500/10',
    border: 'border-sky-500/20 hover:border-sky-400/60',
    badge: 'bg-sky-500/20 text-sky-300',
    questions: '30 questions',
  },
  {
    id: 'Adult',
    emoji: '👤',
    label: 'Adult (26+)',
    desc: 'Work, financial, emotional stability & motivation assessment',
    gradient: 'from-emerald-500/20 to-teal-500/10',
    border: 'border-emerald-500/20 hover:border-emerald-400/60',
    badge: 'bg-emerald-500/20 text-emerald-300',
    questions: '30 questions',
  },
]

export default function AgeSelection({ email, onSelect }) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-sky-500 rounded-full opacity-[0.03] blur-3xl pointer-events-none" />

      <div className="w-full max-w-3xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 text-sky-400 text-sm font-medium px-3 py-1 rounded-full border border-sky-500/30 bg-sky-500/10 mb-4">
            <span>👋</span>
            <span>Welcome, {email}</span>
          </div>
          <h1 className="text-4xl font-black text-white mb-3">Select Your Age Group</h1>
          <p className="text-slate-400 max-w-md mx-auto text-sm leading-relaxed">
            We tailor the psychological questionnaire to your life stage for accurate stress assessment.
          </p>
        </div>

        {/* Cards */}
        <div className="grid md:grid-cols-3 gap-5">
          {AGE_GROUPS.map((opt) => (
            <button
              key={opt.id}
              id={`age-btn-${opt.id.toLowerCase()}`}
              onClick={() => onSelect(opt.id)}
              className={`group relative glass rounded-2xl p-7 text-left border transition-all duration-300
                         hover:-translate-y-1 hover:shadow-xl active:scale-95 ${opt.border}
                         bg-gradient-to-br ${opt.gradient}`}
            >
              <div className="text-4xl mb-5">{opt.emoji}</div>
              <div className={`inline-block text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-md mb-3 ${opt.badge}`}>
                {opt.questions}
              </div>
              <h3 className="text-lg font-bold text-white mb-2">{opt.label}</h3>
              <p className="text-slate-400 text-sm leading-relaxed">{opt.desc}</p>

              <div className="mt-6 flex items-center gap-1 text-sm font-medium text-slate-500 group-hover:text-white transition-colors">
                Start Assessment
                <svg className="w-4 h-4 translate-x-0 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </button>
          ))}
        </div>

        <p className="text-center text-xs text-slate-600 mt-8">
          Your data is processed locally and not stored permanently.
        </p>
      </div>
    </div>
  )
}
