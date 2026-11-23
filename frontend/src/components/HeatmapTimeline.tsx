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

  return (
    <div className="bg-[#121218] border border-[#262636] rounded-xl p-4 sm:p-5 flex flex-col gap-4 shadow-studio-glow">
      {/* Player Header */}
      <div className="flex items-center justify-between text-xs font-mono text-[#7E7E9A]">
        <div className="flex items-center gap-2">
          <span className="text-white font-medium">PRECISION NLE TRIMMER</span>
          {activeClip && (
            <span className="text-[#00F0FF] px-2 py-0.5 rounded bg-[#00F0FF]/10 border border-[#00F0FF]/30">
              {activeClip.title_hook}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <span>
            TIME: <span className="text-white tabular-nums">{formatSec(currentTime)}</span> /{" "}
            <span className="tabular-nums">{formatSec(durationSec)}</span>
          </span>
          <span className="text-[#262636]">|</span>
          <span>
            CLIP DURATION:{" "}
            <span className="text-[#FF2E93] tabular-nums font-bold">
              {formatSec(trimEnd - trimStart)}
            </span>
          </span>
        </div>
      </div>

      {/* HTML5 Video Canvas */}
      <div className="relative aspect-video bg-black rounded-lg overflow-hidden border border-[#262636] group">
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
          <div className="w-full h-full flex flex-col items-center justify-center text-[#505068] text-xs font-mono gap-2">
            <Play className="w-8 h-8 opacity-40" />
            <span>No video loaded. Enter a YouTube URL above.</span>
          </div>
        )}

        {/* Video Overlay Controls */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end justify-between p-4 pointer-events-none">
          <div className="flex items-center gap-2 pointer-events-auto">
            <button
              onClick={togglePlay}
              className="p-2 rounded bg-white text-black hover:bg-[#00F0FF] transition-colors"
            >
              {isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current" />}
            </button>
            <button
              onClick={toggleMute}
              className="p-2 rounded bg-[#1A1A24] text-white hover:bg-[#262636] transition-colors"
            >
              {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
            </button>
          </div>

          <div className="flex items-center gap-2 pointer-events-auto">
            <button
              onClick={() => setIsLooping(!isLooping)}
              className={`px-3 py-1.5 rounded text-xs font-mono flex items-center gap-1.5 border transition-all ${
                isLooping
                  ? "bg-[#FF2E93] border-[#FF2E93] text-black font-bold shadow-neon-pink"
                  : "bg-[#1A1A24] border-[#262636] text-[#7E7E9A] hover:text-white"
              }`}
              title="Infinite Loop Preview: seamlessly loops between clip end and clip start"
            >
              <Repeat className="w-3.5 h-3.5" />
              <span>INFINITE LOOP SIMULATION</span>
            </button>
          </div>
        </div>
      </div>

      {/* Interactive Timeline & Heatmap */}
      <div className="flex flex-col gap-1.5">
        <div
          ref={timelineRef}
          onClick={handleTimelineClick}
          className="relative h-20 bg-[#0A0A0F] border border-[#262636] rounded-lg cursor-pointer overflow-hidden select-none"
        >
          {/* Heatmap SVG Curve */}
          <svg
            viewBox="0 0 1000 50"
            preserveAspectRatio="none"
            className="absolute inset-0 w-full h-full pointer-events-none opacity-60"
          >
            <polyline
              fill="none"
              stroke="#00F0FF"
              strokeWidth="2"
              points={getHeatmapSvgPoints()}
            />
          </svg>

          {/* Active Clip Highlight Zone */}
          {durationSec > 0 && (
            <div
              className="absolute top-0 bottom-0 bg-[#FF2E93]/20 border-x-2 border-[#FF2E93] pointer-events-none"
              style={{
                left: `${(trimStart / durationSec) * 100}%`,
                width: `${((trimEnd - trimStart) / durationSec) * 100}%`,
              }}
            >
              <div className="absolute top-1 left-2 text-[10px] font-mono text-[#FF2E93] font-bold">
                ACTIVE CLIP
              </div>
            </div>
          )}

          {/* Audio Spikes (Red Markers) */}
          {durationSec > 0 &&
            audioSpikes.map((sp, idx) => (
              <div
                key={`a-${idx}`}
                className="absolute top-0 bottom-0 w-[2px] bg-red-500/80 pointer-events-none"
                style={{ left: `${(sp.timestamp_sec / durationSec) * 100}%` }}
                title={`Audio dB spike: ${sp.spike_type} at ${formatSec(sp.timestamp_sec)}`}
              />
            ))}

          {/* Playhead Marker */}
          {durationSec > 0 && (
            <div
              className="absolute top-0 bottom-0 w-[2px] bg-white pointer-events-none shadow-lg z-10"
              style={{ left: `${(currentTime / durationSec) * 100}%` }}
            >
              <div className="w-2.5 h-2.5 bg-white -ml-[4px] rounded-full" />
            </div>
          )}
        </div>

        {/* Legend */}
        <div className="flex items-center justify-between text-[11px] font-mono text-[#505068]">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#00F0FF]" /> Most Replayed Heatmap
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-red-500" /> Audio dB Spikes
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#FF2E93]" /> Active 9:16 Clip Zone
            </span>
          </div>
          <div>Keyboard: Space (Play) | J/L (Seek) | I/O (Trim) | Arrows (0.1s Step)</div>
        </div>
      </div>

      {/* 0.1s Precision Nudge Controls */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-[#1E1E2A]">
        {/* Start Trim Nudge */}
        <div className="flex items-center justify-between bg-[#0A0A0F] border border-[#262636] p-2.5 rounded-lg">
          <div>
            <div className="text-[11px] font-mono text-[#7E7E9A]">TRIM IN-POINT (START)</div>
            <div className="text-sm font-mono font-bold text-white tabular-nums">
              {formatSec(trimStart)}
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => nudgeTrim("start", -0.1)}
              className="px-2 py-1 bg-[#1A1A24] hover:bg-[#262636] text-[#E2E2F0] rounded text-xs font-mono"
            >
              -0.1s
            </button>
            <button
              onClick={() => nudgeTrim("start", +0.1)}
              className="px-2 py-1 bg-[#1A1A24] hover:bg-[#262636] text-[#E2E2F0] rounded text-xs font-mono"
            >
              +0.1s
            </button>
          </div>
        </div>

        {/* End Trim Nudge */}
        <div className="flex items-center justify-between bg-[#0A0A0F] border border-[#262636] p-2.5 rounded-lg">
          <div>
            <div className="text-[11px] font-mono text-[#7E7E9A]">TRIM OUT-POINT (END)</div>
            <div className="text-sm font-mono font-bold text-white tabular-nums">
              {formatSec(trimEnd)}
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => nudgeTrim("end", -0.1)}
              className="px-2 py-1 bg-[#1A1A24] hover:bg-[#262636] text-[#E2E2F0] rounded text-xs font-mono"
            >
              -0.1s
            </button>
            <button
              onClick={() => nudgeTrim("end", +0.1)}
              className="px-2 py-1 bg-[#1A1A24] hover:bg-[#262636] text-[#E2E2F0] rounded text-xs font-mono"
            >
              +0.1s
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
