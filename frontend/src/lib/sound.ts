/**
 * Report-ready sound: short, subtle, non-jarring.
 * Generated via Web Audio API. Two-tone chime.
 * Throttled/queued so only one sound plays at a time when multiple reports become ready.
 */

let lastPlayTime = 0;
const MIN_INTERVAL_MS = 600;
let queueTimeout: ReturnType<typeof setTimeout> | null = null;

function playOnce(): void {
  try {
    const ctx = new (window.AudioContext ?? (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.2, ctx.currentTime);
    gain.connect(ctx.destination);

    const playTone = (frequency: number, startTime: number, duration: number) => {
      const osc = ctx.createOscillator();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(frequency, startTime);
      osc.connect(gain);
      osc.start(startTime);
      osc.stop(startTime + duration);
    };

    playTone(660, ctx.currentTime, 0.08);
    playTone(880, ctx.currentTime + 0.1, 0.12);
  } catch {
    // Ignore (e.g. unsupported or autoplay blocked)
  }
}

/**
 * Play the report-ready sound once. If called in quick succession, queues so only one
 * plays at a time and playback does not overlap (per contract).
 */
export function playReportReadySound(): void {
  const now = Date.now();
  if (now - lastPlayTime >= MIN_INTERVAL_MS) {
    lastPlayTime = now;
    playOnce();
    return;
  }
  if (queueTimeout != null) return;
  queueTimeout = setTimeout(() => {
    queueTimeout = null;
    lastPlayTime = Date.now();
    playOnce();
  }, MIN_INTERVAL_MS - (now - lastPlayTime));
}
