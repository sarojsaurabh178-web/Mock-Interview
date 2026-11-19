import React, { useState, useRef, useEffect } from 'react';
import './AudioTracker.css';

/**
 * AudioTracker Component:
 * Interactive audio player & scrubber that allows the candidate to listen back
 * to their recorded microphone audio with real-time waveform progress tracking.
 */
export function AudioTracker({ audioUrl }) {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1.0);

  // Reset playback state when audioUrl changes
  useEffect(() => {
    setIsPlaying(false);
    setCurrentTime(0);
    setDuration(0);
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
  }, [audioUrl]);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play().then(() => {
        setIsPlaying(true);
      }).catch((err) => {
        console.error('Audio playback error:', err);
        setIsPlaying(false);
      });
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      const d = audioRef.current.duration;
      // Handle infinity or NaN durations that can occur with WebM blobs
      if (Number.isFinite(d)) {
        setDuration(d);
      } else {
        // Fallback probe
        audioRef.current.currentTime = 1e101;
        audioRef.current.ontimeupdate = () => {
          audioRef.current.ontimeupdate = handleTimeUpdate;
          setDuration(audioRef.current.duration);
          audioRef.current.currentTime = 0;
        };
      }
    }
  };

  const handleEnded = () => {
    setIsPlaying(false);
    setCurrentTime(0);
    if (audioRef.current) {
      audioRef.current.currentTime = 0;
    }
  };

  const handleSeek = (e) => {
    const newTime = parseFloat(e.target.value);
    setCurrentTime(newTime);
    if (audioRef.current) {
      audioRef.current.currentTime = newTime;
    }
  };

  const handleRestart = () => {
    if (audioRef.current) {
      audioRef.current.currentTime = 0;
      setCurrentTime(0);
      if (!isPlaying) {
        audioRef.current.play().then(() => setIsPlaying(true));
      }
    }
  };

  const toggleSpeed = () => {
    const nextRate = playbackRate === 1.0 ? 1.25 : playbackRate === 1.25 ? 1.5 : 1.0;
    setPlaybackRate(nextRate);
    if (audioRef.current) {
      audioRef.current.playbackRate = nextRate;
    }
  };

  const formatSec = (secs) => {
    if (!secs || isNaN(secs) || !Number.isFinite(secs)) return '00:00';
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  };

  const progressPercent = duration > 0 ? Math.min(100, (currentTime / duration) * 100) : 0;

  if (!audioUrl) return null;

  return (
    <div className="audio-tracker-wrapper">
      <audio
        ref={audioRef}
        src={audioUrl}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={handleEnded}
        preload="metadata"
      />

      <div className="audio-tracker-controls">
        {/* Play/Pause Button */}
        <button
          type="button"
          className={`audio-tracker-play-btn ${isPlaying ? 'playing' : ''}`}
          onClick={togglePlay}
          title={isPlaying ? 'Pause' : 'Play recorded answer'}
          aria-label={isPlaying ? 'Pause' : 'Play recorded answer'}
        >
          {isPlaying ? (
            <span className="icon-pause">❚❚</span>
          ) : (
            <span className="icon-play">▶</span>
          )}
        </button>

        {/* Audio Scrubber & Wave Track */}
        <div className="audio-tracker-track-area">
          <div className="audio-tracker-meta">
            <span className="audio-tracker-label">
              <span className="audio-dot" />
              Recorded Audio Playback
            </span>
            <span className="audio-tracker-timer">
              {formatSec(currentTime)} / {formatSec(duration)}
            </span>
          </div>

          <div className="audio-tracker-slider-container">
            <div
              className="audio-tracker-progress-fill"
              style={{ width: `${progressPercent}%` }}
            />
            <input
              type="range"
              className="audio-tracker-range"
              min={0}
              max={duration || 1}
              step={0.05}
              value={currentTime}
              onChange={handleSeek}
              aria-label="Seek audio playback"
            />
          </div>
        </div>

        {/* Speed Multiplier & Restart */}
        <div className="audio-tracker-actions">
          <button
            type="button"
            className="audio-tracker-mini-btn"
            onClick={toggleSpeed}
            title="Toggle playback speed"
          >
            {playbackRate}x
          </button>
          <button
            type="button"
            className="audio-tracker-mini-btn"
            onClick={handleRestart}
            title="Replay from start"
          >
            ↺
          </button>
        </div>
      </div>
    </div>
  );
}

export default AudioTracker;
