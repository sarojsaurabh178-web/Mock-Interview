export function CameraPreviewCard({
  recording,
  seconds,
  formatTime,
  micEnabled = true,
  onToggleMic,
  cameraEnabled = true,
  onToggleCamera,
}) {
  return (
    <div className="camera-panel">
      <div className="camera-top">
        <span>
          <i className={recording ? 'recording-dot' : ''} />
          {recording ? ' RECORDING' : ' CAMERA PREVIEW'}
        </span>
        <span className="camera-status">
          {recording ? formatTime(seconds) : '● Ready when you are'}
        </span>
      </div>
      <div className="camera-stage">
        <div className="camera-placeholder">
          <div className="camera-orbit" />
          <div className="camera-person">
            <div className="camera-head" />
            <div className="camera-torso" />
          </div>
          <div className="camera-message">
            <strong>{recording ? 'You’re doing great.' : 'Your camera preview'}</strong>
            <span>
              {recording
                ? 'Keep going — take your time.'
                : 'This is just for you. Take a breath and begin when you’re ready.'}
            </span>
          </div>
        </div>
        <div className="camera-controls">
          <button
            type="button"
            aria-label="Microphone"
            style={{ opacity: micEnabled ? 1 : 0.4 }}
            onClick={onToggleMic}
            title={micEnabled ? 'Mute microphone' : 'Unmute microphone'}
          >
            ♩
          </button>
          <button
            type="button"
            aria-label="Camera"
            style={{ opacity: cameraEnabled ? 1 : 0.4 }}
            onClick={onToggleCamera}
            title={cameraEnabled ? 'Turn off camera' : 'Turn on camera'}
          >
            ▣
          </button>
          <span>Camera & microphone are only used in your browser.</span>
          <button type="button" className="control-more" aria-label="More settings">
            •••
          </button>
        </div>
      </div>
    </div>
  )
}

export default CameraPreviewCard
