import React, { useEffect, useRef, useCallback } from 'react';
import {
  Play,
  Pause,
  FastForward,
  Rewind,
  Volume2,
  Clock,
} from 'lucide-react';
import { useUIStore } from '../../store';

export const Timeline: React.FC = () => {
  const {
    audioAnalysis,
    currentTime,
    setCurrentTime,
    isPlaying,
    setIsPlaying,
    duration,
  } = useUIStore();

  const timelineTrackRef = useRef<HTMLDivElement>(null);
  const isScrubbingRef = useRef<boolean>(false);

  const beats = audioAnalysis?.beat_timestamps || [];
  const onsetEnvelope = audioAnalysis?.onset_envelope || [];

  // ---------------------------------------------------------------------------
  // Smooth Playback Loop via requestAnimationFrame
  // ---------------------------------------------------------------------------
  useEffect(() => {
    if (!isPlaying) return;

    let lastTimestamp = performance.now();
    let animId: number;

    const tick = (now: number) => {
      const deltaSec = (now - lastTimestamp) / 1000.0;
      lastTimestamp = now;

      setCurrentTime((currentTime + deltaSec) % duration);
      animId = requestAnimationFrame(tick);
    };

    animId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animId);
  }, [isPlaying, currentTime, duration, setCurrentTime]);

  // ---------------------------------------------------------------------------
  // Timeline Scrubbing / Seeking Interaction
  // ---------------------------------------------------------------------------
  const handleSeekFromEvent = useCallback(
    (clientX: number) => {
      if (!timelineTrackRef.current) return;
      const rect = timelineTrackRef.current.getBoundingClientRect();
      const rawX = clientX - rect.left;
      const clampedX = Math.max(0, Math.min(rect.width, rawX));
      const newTime = (clampedX / rect.width) * duration;
      setCurrentTime(newTime);
    },
    [duration, setCurrentTime]
  );

  const handleMouseDown = (e: React.MouseEvent) => {
    isScrubbingRef.current = true;
    handleSeekFromEvent(e.clientX);

    const onMouseMove = (ev: MouseEvent) => {
      if (isScrubbingRef.current) {
        handleSeekFromEvent(ev.clientX);
      }
    };

    const onMouseUp = () => {
      isScrubbingRef.current = false;
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  };

  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className="bg-zinc-950 border border-zinc-800 rounded-xl p-3.5 flex flex-col gap-2.5 shadow-xl select-none">
      {/* Top Controls & Transport Bar */}
      <div className="flex items-center justify-between border-b border-zinc-800/80 pb-2">
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setCurrentTime(0)}
            title="Rebobinar al inicio"
            className="p-1.5 hover:bg-zinc-800 text-zinc-400 hover:text-white rounded transition"
          >
            <Rewind className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            title={isPlaying ? 'Pausar (Espacio)' : 'Reproducir (Espacio)'}
            className="p-1.5 bg-cyan-500 hover:bg-cyan-400 text-black font-semibold rounded-lg shadow transition active:scale-95"
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
          </button>
          <button
            onClick={() => setCurrentTime(duration)}
            title="Ir al final"
            className="p-1.5 hover:bg-zinc-800 text-zinc-400 hover:text-white rounded transition"
          >
            <FastForward className="w-4 h-4" />
          </button>

          <div className="flex items-center gap-1.5 font-mono text-xs text-zinc-300 ml-2 bg-zinc-900 px-2.5 py-1 rounded border border-zinc-800">
            <Clock className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-cyan-300 font-semibold">{currentTime.toFixed(2)}s</span>
            <span className="text-zinc-600">/</span>
            <span>{duration.toFixed(2)}s</span>
          </div>
        </div>

        <div className="flex items-center gap-3 text-xs text-zinc-400 font-mono">
          <div className="flex items-center gap-1.5 bg-zinc-900/60 px-2 py-0.5 rounded border border-zinc-800">
            <Volume2 className="w-3.5 h-3.5 text-cyan-400" />
            <span>BPM: {audioAnalysis?.bpm ? audioAnalysis.bpm.toFixed(1) : '128.0'}</span>
          </div>
          <span className="text-zinc-700">|</span>
          <span>4/4 Time Signature</span>
          <span className="text-zinc-700">|</span>
          <span className="text-emerald-400">Audio Sync OK</span>
        </div>
      </div>

      {/* Multi-Track Lanes & Scrubber Container */}
      <div
        ref={timelineTrackRef}
        onMouseDown={handleMouseDown}
        className="relative bg-zinc-900/80 rounded-lg p-2.5 overflow-hidden flex flex-col gap-2 cursor-pointer border border-zinc-800"
      >
        {/* Playhead Vertical Cursor */}
        <div
          style={{ left: `${progressPercent}%` }}
          className="absolute top-0 bottom-0 w-0.5 bg-amber-400 z-30 pointer-events-none shadow-[0_0_8px_rgba(251,191,36,0.8)]"
        >
          <div className="w-2.5 h-2.5 bg-amber-400 rounded-full -translate-x-[4px] -translate-y-1 shadow" />
        </div>

        {/* Track 1: Audio Waveform & Beats */}
        <div className="h-9 bg-zinc-950/70 rounded border border-zinc-800/80 relative flex items-center px-2 overflow-hidden">
          <span className="text-[10px] text-zinc-500 font-mono absolute left-2 z-10 pointer-events-none">
            AUDIO TRACK ({beats.length} BEATS)
          </span>

          {/* Procedural Waveform Bars */}
          <div className="absolute inset-0 flex items-center justify-around opacity-30 px-1 pointer-events-none">
            {onsetEnvelope.length > 0
              ? onsetEnvelope.map((amp, i) => (
                  <div
                    key={i}
                    style={{ height: `${Math.max(15, amp * 100)}%` }}
                    className="w-1 bg-cyan-400 rounded-sm"
                  />
                ))
              : Array.from({ length: 32 }).map((_, i) => (
                  <div
                    key={i}
                    style={{ height: `${20 + Math.sin(i * 0.5) * 35}%` }}
                    className="w-1 bg-cyan-400 rounded-sm"
                  />
                ))}
          </div>

          {/* Beat Markers */}
          <div className="w-full h-full relative pointer-events-none">
            {beats.map((b, idx) => {
              const posPercent = (b / duration) * 100;
              return (
                <div
                  key={idx}
                  style={{ left: `${posPercent}%` }}
                  className="absolute top-0 bottom-0 w-0.5 bg-cyan-400/80"
                  title={`Beat: ${b}s`}
                />
              );
            })}
          </div>
        </div>

        {/* Track 2: CineCamera Choreography */}
        <div className="h-8 bg-zinc-950/70 rounded border border-zinc-800/80 relative flex items-center px-2 overflow-hidden">
          <span className="text-[10px] text-zinc-500 font-mono absolute left-2 z-10 pointer-events-none">
            CINECAMERA
          </span>
          <div className="w-full h-full relative pointer-events-none">
            <div className="absolute top-1 bottom-1 left-0 w-[40%] bg-amber-500/20 border border-amber-500/40 rounded px-1.5 text-[9px] text-amber-300 flex items-center font-mono">
              Dramatic Orbit (Keyframes 1-4)
            </div>
            <div className="absolute top-1 bottom-1 left-[42%] right-0 bg-amber-500/10 border border-amber-500/30 rounded px-1.5 text-[9px] text-amber-400 flex items-center font-mono">
              Spiral Ascent & Cut
            </div>
          </div>
        </div>

        {/* Track 3: 3D Mocap Dance Motion */}
        <div className="h-8 bg-zinc-950/70 rounded border border-zinc-800/80 relative flex items-center px-2 overflow-hidden">
          <span className="text-[10px] text-zinc-500 font-mono absolute left-2 z-10 pointer-events-none">
            MOCAP DANCE
          </span>
          <div className="w-full h-full relative pointer-events-none">
            <div className="absolute top-1 bottom-1 left-0 right-0 bg-emerald-500/15 border border-emerald-500/30 rounded px-2 text-[9px] text-emerald-300 flex items-center font-mono">
              GVHMR Biped Dance Loop (Synced to Beats)
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Timeline;
