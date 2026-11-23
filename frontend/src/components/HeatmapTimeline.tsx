"use client";

import React, { useEffect, useRef, useState } from "react";
import {
  Play,
  Pause,
  RotateCcw,
  Volume2,
  VolumeX,
  Repeat,
  ChevronLeft,
  ChevronRight,
  Flame,
  Zap,
} from "lucide-react";
import { AudioSpike, ClipCandidate, HeatmapPoint, VisualSpike } from "@/types";

interface HeatmapTimelineProps {
  videoSrc: string;
  durationSec: number;
  heatmap: HeatmapPoint[];
  audioSpikes: AudioSpike[];
  visualSpikes: VisualSpike[];
  activeClip: ClipCandidate | null;
  onUpdateTrim: (clipId: string, startSec: number, endSec: number) => void;
}

export const HeatmapTimeline: React.FC<HeatmapTimelineProps> = ({
  videoSrc,
  durationSec,
  heatmap,
  audioSpikes,
  visualSpikes,
  activeClip,
  onUpdateTrim,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const timelineRef = useRef<HTMLDivElement>(null);

  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isLooping, setIsLooping] = useState(false);

  // Local trim boundaries
  const [trimStart, setTrimStart] = useState(activeClip ? activeClip.start_sec : 0);
  const [trimEnd, setTrimEnd] = useState(activeClip ? activeClip.end_sec : Math.min(30, durationSec));

  useEffect(() => {
    if (activeClip) {
      setTrimStart(activeClip.start_sec);
      setTrimEnd(activeClip.end_sec);
      if (videoRef.current) {
        videoRef.current.currentTime = activeClip.start_sec;
      }
    }
  }, [activeClip]);

  // Video Time Update & Infinite Loop Simulation
  const handleTimeUpdate = () => {
    if (!videoRef.current) return;
    const t = videoRef.current.currentTime;
    setCurrentTime(t);

    if (isLooping) {
      // In loop mode: when we reach within 0.1s of trimEnd, seamless loop jump back to trimStart
      if (t >= trimEnd) {
        videoRef.current.currentTime = trimStart;
      }
    }
  };

  // Keyboard Shortcuts (Space, J, K, L, I, O, Left/Right arrow)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if typing in an input
      if (["INPUT", "TEXTAREA"].includes((e.target as HTMLElement)?.tagName)) return;

      const vid = videoRef.current;
      if (!vid) return;

      switch (e.code) {
        case "Space":
          e.preventDefault();
          if (vid.paused) vid.play();
          else vid.pause();
          break;
        case "KeyK":
          if (vid.paused) vid.play();
          else vid.pause();
          break;
        case "KeyJ":
          vid.currentTime = Math.max(0, vid.currentTime - 2);
          break;
        case "KeyL":
          vid.currentTime = Math.min(durationSec, vid.currentTime + 2);
          break;
        case "KeyI":
          // Set IN point
          nudgeTrim("start", vid.currentTime - trimStart);
          break;
        case "KeyO":
          // Set OUT point
          nudgeTrim("end", vid.currentTime - trimEnd);
          break;
        case "ArrowLeft":
          e.preventDefault();
          vid.currentTime = Math.max(0, vid.currentTime - 0.1);
          break;
        case "ArrowRight":
          e.preventDefault();
          vid.currentTime = Math.min(durationSec, vid.currentTime + 0.1);
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [durationSec, trimStart, trimEnd]);

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (videoRef.current.paused) {
      videoRef.current.play();
      setIsPlaying(true);
    } else {
      videoRef.current.pause();
      setIsPlaying(false);
    }
  };

  const toggleMute = () => {
    if (!videoRef.current) return;
    videoRef.current.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const nudgeTrim = (handle: "start" | "end", delta: number) => {
    if (!activeClip) return;
    if (handle === "start") {
      const next = Math.max(0, Math.min(trimEnd - 1.0, trimStart + delta));
      setTrimStart(next);
      onUpdateTrim(activeClip.clip_id, next, trimEnd);
    } else {
      const next = Math.min(durationSec, Math.max(trimStart + 1.0, trimEnd + delta));
      setTrimEnd(next);
      onUpdateTrim(activeClip.clip_id, trimStart, next);
    }
  };

  const handleTimelineClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!timelineRef.current || !videoRef.current || durationSec <= 0) return;
    const rect = timelineRef.current.getBoundingClientRect();
    const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const targetTime = ratio * durationSec;
    videoRef.current.currentTime = targetTime;
  };

  const formatSec = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    const ms = Math.floor((s - Math.floor(s)) * 10);
    return `${m}:${sec.toString().padStart(2, "0")}.${ms}`;
  };

  // Convert Heatmap to SVG Polyline Points
  const getHeatmapSvgPoints = () => {
    if (!heatmap || heatmap.length === 0 || durationSec <= 0) return "";
    return heatmap
      .map((hp) => {
        const x = (hp.start_sec / durationSec) * 1000;
        const y = 50 - hp.intensity * 45; // 0 intensity = bottom (y=50), 1.0 = top (y=5)
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(" ");
  };

  // Generate Simulated Audio Waveform Bars (80 bars across timeline)
  const getAudioWaveformBars = () => {
    if (durationSec <= 0) return [];
    const barsCount = 80;
    const bars = [];
    for (let i = 0; i < barsCount; i++) {
      const timeAtBar = (i / barsCount) * durationSec;
      const nearSpike = audioSpikes.some(
        (sp) => Math.abs(sp.timestamp_sec - timeAtBar) < Math.max(1.5, durationSec * 0.02)
      );
      // Pseudo-random deterministic amplitude
      const seed = Math.sin(i * 12.9898 + 78.233) * 43758.5453;
      const noise = seed - Math.floor(seed);
      const baseHeight = 5 + noise * 14;
      const height = nearSpike ? Math.min(32, baseHeight * 2.2) : baseHeight;
      const x = (i / barsCount) * 1000 + 4;
      bars.push({ x, height, isHot: nearSpike });
    }
    return bars;
  };

  return (
    <div className="bg-studio-900 border border-studio-700/80 rounded-lg p-4 sm:p-5 flex flex-col gap-4 shadow-studio-card">
      {/* Player Header */}
      <div className="flex items-center justify-between text-xs font-mono text-studio-400">
        <div className="flex items-center gap-2">
          <span className="text-studio-200 font-medium">Precision trimmer</span>
          {activeClip && (
            <span className="text-tally-amber px-2 py-0.5 rounded bg-tally-amber/10 border border-tally-amber/30 text-xs font-mono font-medium">
              {activeClip.title_hook}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <span>
            Time: <span className="text-studio-100 tabular-nums">{formatSec(currentTime)}</span> /{" "}
            <span className="tabular-nums text-studio-400">{formatSec(durationSec)}</span>
          </span>
          <span className="text-studio-700">|</span>
          <span>
            Clip duration:{" "}
            <span className="text-tally-amber tabular-nums font-medium">
              {formatSec(trimEnd - trimStart)}
            </span>
          </span>
        </div>
      </div>

      {/* HTML5 Video Canvas */}
      <div className="relative aspect-video bg-black rounded-md overflow-hidden border border-studio-800 group">
        {videoSrc ? (
          <video
            ref={videoRef}
            src={videoSrc}
            onTimeUpdate={handleTimeUpdate}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            className="w-full h-full object-contain"
          />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center text-studio-500 text-xs font-mono gap-2">
            <Play className="w-8 h-8 opacity-40 text-studio-600" />
            <span>No video loaded. Enter a YouTube URL above.</span>
          </div>
        )}

        {/* Video Overlay Controls */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end justify-between p-4 pointer-events-none">
          <div className="flex items-center gap-2 pointer-events-auto">
            <button
              onClick={togglePlay}
              className="p-2 rounded bg-studio-100 text-studio-950 hover:bg-white transition-colors"
            >
              {isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current" />}
            </button>
            <button
              onClick={toggleMute}
              className="p-2 rounded bg-studio-800 text-studio-200 hover:bg-studio-700 transition-colors"
            >
              {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
            </button>
          </div>

          <div className="flex items-center gap-2 pointer-events-auto">
            <button
              onClick={() => setIsLooping(!isLooping)}
              className={`px-3 py-1.5 rounded text-xs font-mono flex items-center gap-1.5 border transition-colors ${
                isLooping
                  ? "bg-tally-amber border-tally-amber text-studio-950 font-medium"
                  : "bg-studio-800 border-studio-700 text-studio-300 hover:text-white"
              }`}
              title="Infinite loop preview: seamlessly loops between clip end and clip start"
            >
              <Repeat className="w-3.5 h-3.5" />
              <span>Loop range</span>
            </button>
          </div>
        </div>
      </div>

      {/* Interactive Timeline & Heatmap */}
      <div className="flex flex-col gap-1.5">
        <div
          ref={timelineRef}
          onClick={handleTimelineClick}
          className="relative h-20 bg-studio-950 border border-studio-800 rounded cursor-pointer overflow-hidden select-none"
        >
          {/* Simulated DAW / NLE Audio Waveform Track */}
          <svg
            viewBox="0 0 1000 50"
            preserveAspectRatio="none"
            className="absolute inset-0 w-full h-full pointer-events-none opacity-40"
          >
            {getAudioWaveformBars().map((bar, idx) => (
              <line
                key={idx}
                x1={bar.x}
                y1={48 - bar.height}
                x2={bar.x}
                y2={48}
                stroke={bar.isHot ? "#F59E0B" : "#475569"}
                strokeWidth="5"
                strokeLinecap="round"
              />
            ))}
          </svg>

          {/* Heatmap SVG Curve */}
          <svg
            viewBox="0 0 1000 50"
            preserveAspectRatio="none"
            className="absolute inset-0 w-full h-full pointer-events-none opacity-60"
          >
            <polyline
              fill="none"
              stroke="#94A3B8"
              strokeWidth="2.5"
              points={getHeatmapSvgPoints()}
            />
          </svg>

          {/* Active Clip Highlight Zone */}
          {durationSec > 0 && (
            <div
              className="absolute top-0 bottom-0 bg-tally-amber/15 border-x-2 border-tally-amber pointer-events-none"
              style={{
                left: `${(trimStart / durationSec) * 100}%`,
                width: `${((trimEnd - trimStart) / durationSec) * 100}%`,
              }}
            >
              <div className="absolute top-1 left-2 text-[10px] font-mono text-tally-amber font-medium">
                Active range
              </div>
            </div>
          )}

          {/* Audio Spikes (Red Markers) */}
          {durationSec > 0 &&
            audioSpikes.map((sp, idx) => (
              <div
                key={`a-${idx}`}
                className="absolute top-0 bottom-0 w-[2px] bg-tally-red/70 pointer-events-none"
                style={{ left: `${(sp.timestamp_sec / durationSec) * 100}%` }}
                title={`Audio spike: ${sp.spike_type} at ${formatSec(sp.timestamp_sec)}`}
              />
            ))}

          {/* Playhead Marker */}
          {durationSec > 0 && (
            <div
              className="absolute top-0 bottom-0 w-[2px] bg-white pointer-events-none shadow-md z-10"
              style={{ left: `${(currentTime / durationSec) * 100}%` }}
            >
              <div className="w-2.5 h-2.5 bg-white -ml-[4px] rounded-full shadow" />
            </div>
          )}
        </div>

        {/* Legend */}
        <div className="flex items-center justify-between text-[11px] font-mono text-studio-500">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-slate-400" /> Retention curve
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-studio-600" /> Audio waveform
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-tally-red/70" /> Audio spikes
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-tally-amber" /> Active clip zone
            </span>
          </div>
          <div>Shortcuts: Space (Play) | J/L (Seek) | I/O (Trim) | Arrows (0.1s step)</div>
        </div>
      </div>

      {/* 0.1s Precision Nudge Controls */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-studio-800">
        {/* Start Trim Nudge */}
        <div className="flex items-center justify-between bg-studio-950 border border-studio-800 p-2.5 rounded">
          <div>
            <div className="text-[11px] font-mono text-studio-400">In-point (start)</div>
            <div className="text-sm font-mono font-medium text-studio-100 tabular-nums">
              {formatSec(trimStart)}
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => nudgeTrim("start", -0.1)}
              className="px-2.5 py-1 bg-studio-800 hover:bg-studio-700 text-studio-200 rounded text-xs font-mono border border-studio-700/60 transition-colors"
            >
              -0.1s
            </button>
            <button
              onClick={() => nudgeTrim("start", +0.1)}
              className="px-2.5 py-1 bg-studio-800 hover:bg-studio-700 text-studio-200 rounded text-xs font-mono border border-studio-700/60 transition-colors"
            >
              +0.1s
            </button>
          </div>
        </div>

        {/* End Trim Nudge */}
        <div className="flex items-center justify-between bg-studio-950 border border-studio-800 p-2.5 rounded">
          <div>
            <div className="text-[11px] font-mono text-studio-400">Out-point (end)</div>
            <div className="text-sm font-mono font-medium text-studio-100 tabular-nums">
              {formatSec(trimEnd)}
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => nudgeTrim("end", -0.1)}
              className="px-2.5 py-1 bg-studio-800 hover:bg-studio-700 text-studio-200 rounded text-xs font-mono border border-studio-700/60 transition-colors"
            >
              -0.1s
            </button>
            <button
              onClick={() => nudgeTrim("end", +0.1)}
              className="px-2.5 py-1 bg-studio-800 hover:bg-studio-700 text-studio-200 rounded text-xs font-mono border border-studio-700/60 transition-colors"
            >
              +0.1s
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
