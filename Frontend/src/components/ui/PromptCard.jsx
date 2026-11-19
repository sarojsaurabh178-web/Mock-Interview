import React from 'react';
import { Orb } from '@yogesharc/thinking-orbs';

export function PromptCard({
  isInInterviewRoom = false,
  activeQuestion,
  recording,
  onScheduleInterview,
  onRecordOrStop,
  onFinish,
  evaluation = null,
  isAnalyzing = false,
  onPlayAudio = null,
  isPlayingAudio = false,
}) {
  if (!isInInterviewRoom) {
    return (
      <div className="prompt-panel">
        <div className="prompt-top">
          <span className="eyebrow">PREPARATION & SETUP</span>
          <span className="prompt-tag">Step 1 of 2</span>
        </div>

        <h2>Ready for your personalized mock interview?</h2>
        <p>
          Schedule your interview first by providing the target Job Description and your Resume.
          The AI will analyze your documents, match skills, and prepare tailored questions before entering your live audio interview room.
        </p>

        <div className="prompt-tip">
          <span>✦</span>
          <div>
            <strong>How It Works</strong>
            <p>
              1. Click "Schedule Interview" below.<br />
              2. Upload or paste the Job Description & Resume.<br />
              3. The AI matches competencies, generates your plan, and navigates you directly into the live Interview Room.
            </p>
          </div>
        </div>

        <div className="practice-actions">
          <button
            className="primary-button"
            onClick={onScheduleInterview}
            style={{ width: '100%', justifyContent: 'center', display: 'inline-flex', alignItems: 'center', gap: '8px' }}
          >
            <Orb state="idle" variant="blink" size={16} />
            Schedule Interview ↗
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="prompt-panel">
      <div className="prompt-top">
        <span className="eyebrow">
          {activeQuestion?.question_number ? `QUESTION #${activeQuestion.question_number}` : 'ACTIVE QUESTION'} • LIVE INTERVIEW
        </span>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {onPlayAudio && (
            <button
              type="button"
              className="text-link"
              onClick={onPlayAudio}
              disabled={isPlayingAudio}
              style={{ fontSize: '10px', color: '#7258cc', display: 'flex', alignItems: 'center', gap: '4px' }}
              title="Hear interviewer speak the question"
            >
              {isPlayingAudio ? '🔊 Speaking...' : '🔈 Read Aloud'}
            </button>
          )}
          <span className="prompt-tag">{activeQuestion?.round_name || activeQuestion?.category || 'Behavioral'}</span>
        </div>
      </div>

      <h2>{activeQuestion?.question_text || activeQuestion?.title || 'Tell me about yourself.'}</h2>
      <p>{activeQuestion?.intent || activeQuestion?.detail || 'A concise story that connects your past, present, and next step.'}</p>

      {/* AI Evaluation / Feedback Block */}
      {isAnalyzing && (
        <div className="prompt-tip" style={{ borderColor: '#9d86ec', background: '#faf9fd' }}>
          <span>⏳</span>
          <div>
            <strong>Analyzing Spoken Answer...</strong>
            <p>Evaluating STAR delivery, speech cadence, and technical depth.</p>
          </div>
        </div>
      )}

      {evaluation && !isAnalyzing && (
        <div className="prompt-tip" style={{ borderLeft: '3px solid #7258cc', background: '#fbfaff' }}>
          <span>✦</span>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
              <strong>Answer Score: {evaluation.score}/100</strong>
              <span style={{ fontSize: '10px', color: '#624ca7', fontWeight: 'bold' }}>
                Relevance: {evaluation.relevance_score}%
              </span>
            </div>
            <p style={{ margin: '3px 0' }}>{evaluation.feedback}</p>
            {evaluation.suggested_followup && (
              <div style={{ marginTop: '6px', fontSize: '11px', color: '#40394c' }}>
                <em>Follow-up: "{evaluation.suggested_followup}"</em>
              </div>
            )}
          </div>
        </div>
      )}

      {!evaluation && !isAnalyzing && (
        <div className="prompt-tip">
          <span>✦</span>
          <div>
            <strong>Audio Interview Tip</strong>
            <p>Speak clearly at an even pace. Highlight the action you took and quantify the final result.</p>
          </div>
        </div>
      )}

      <div className="practice-actions">
        <button
          className={`primary-button ${recording ? 'recording-button' : ''}`}
          onClick={onRecordOrStop}
        >
          {recording ? '■   Stop & Submit Answer' : '◉    Record Answer'}
        </button>
        <button className="finish-button" onClick={onFinish}>
          Finish session <span>↗</span>
        </button>
      </div>
    </div>
  )
}

export default PromptCard
