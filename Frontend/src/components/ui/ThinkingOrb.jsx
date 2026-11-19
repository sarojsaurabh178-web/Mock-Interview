import React from 'react';
import { Orb } from '@yogesharc/thinking-orbs';
import './ThinkingOrb.css';

/**
 * ThinkingOrb Component:
 * Powered by official @yogesharc/thinking-orbs package.
 * Seamlessly transitions between states:
 * - 'idle'       -> Orb state="idle" variant="blink"
 * - 'listening'  -> Orb state="using" variant="record"
 * - 'speaking'   -> Orb state="working" variant="gyro"
 * - 'thinking'   -> Orb state="reasoning" variant="twins"
 * - 'searching'  -> Orb state="searching" variant="lighthouse"
 * - 'compacting' -> Orb state="compacting" variant="fuse"
 */
export function ThinkingOrb({
  state = 'idle',
  label = null,
  showPill = true,
  size = 48,
  className = '',
}) {
  // Map application interview state to @yogesharc/thinking-orbs state & variant
  const orbConfig = {
    idle: {
      state: 'idle',
      variant: 'blink',
      color: '#8b5cf6',
      label: 'AI Interviewer • Ready',
    },
    listening: {
      state: 'using',
      variant: 'record',
      color: '#f43f5e',
      label: 'Listening to your answer...',
    },
    speaking: {
      state: 'working',
      variant: 'gyro',
      color: '#fbbf24',
      label: 'AI Interviewer • Speaking...',
    },
    thinking: {
      state: 'reasoning',
      variant: 'twins',
      color: '#38bdf8',
      label: 'Evaluating answer & metrics...',
    },
    searching: {
      state: 'searching',
      variant: 'lighthouse',
      color: '#34d399',
      label: 'Analyzing JD & matching competencies...',
    },
    compacting: {
      state: 'compacting',
      variant: 'fuse',
      color: '#a78bfa',
      label: 'Synthesizing performance report...',
    },
  };

  const current = orbConfig[state] || orbConfig.idle;
  const activeLabel = label || current.label;

  // Dynamic animation speed multiplier during vocal speech / analysis
  const currentSpeed =
    state === 'speaking' ? 2.0 :
    state === 'listening' ? 1.5 :
    state === 'thinking' ? 1.6 :
    1.0;

  return (
    <div
      className={`thinking-orb-container state-${state} ${className}`}
      style={{ color: current.color }}
    >
      <div className="thinking-orb-stage">
        {/* Soft atmospheric backlight halo */}
        <div className="orb-halo" style={{ background: current.color }} />

        {/* Ambient breathing aura glow */}
        <div className="orb-glow" />

        {/* Dynamic soundwave audio reverberation rings for speech */}
        <div className="orb-ring orb-ring-speech" />
        <div className="orb-ring orb-ring-secondary" />

        {/* Official Thinking Orb from @yogesharc/thinking-orbs */}
        <div className="official-orb-wrapper">
          <Orb
            state={current.state}
            variant={current.variant}
            size={size}
            speed={currentSpeed}
            className="thinking-orb-svg"
          />
        </div>
      </div>

      {/* Dynamic Status Pill */}
      {showPill && (
        <div className="orb-status-pill">
          <span className="orb-status-dot" style={{ background: current.color }} />
          <span>{activeLabel}</span>
          {state === 'speaking' && (
            <span className="orb-voice-waves">
              <span className="wave-bar" />
              <span className="wave-bar" />
              <span className="wave-bar" />
            </span>
          )}
        </div>
      )}
    </div>
  );
}

export default ThinkingOrb;
