"use client";

import React from "react";
import { Play, CheckCircle, Loader2, FileText } from "lucide-react";
import { ClipCandidate } from "@/types";

interface ClipCandidateCardProps {
  clip: ClipCandidate;
  index: number;
  isActive: boolean;
  onSelect: () => void;
  onRender: () => void;
  onOpenUploadKit: () => void;
  isRendering: boolean;
}

export const ClipCandidateCard: React.FC<ClipCandidateCardProps> = ({
  clip,
  index,
  isActive,
  onSelect,
  onRender,
  onOpenUploadKit,
  isRendering,
}) => {
  const duration = (clip.end_sec - clip.start_sec).toFixed(1);

  // Compute composite score
  const v = clip.virality;
  const overallScore = v
    ? Math.round(
        v.three_second_visual_hook * 0.3 +
          v.replay_loop_factor * 0.25 +
          v.debate_comment_bait_potential * 0.25 +
          v.payoff_speed * 0.2
      )
    : Math.round(clip.virality_score || 0);

  const isCompleted = clip.status === "completed";

  return (
    <div
      onClick={onSelect}
      className={`p-4 rounded-xl border transition-all duration-150 cursor-pointer flex flex-col gap-3 group hover:-translate-y-0.5 ${
        isActive
          ? "bg-studio-850 border-tally-amber shadow-studio-card ring-1 ring-tally-amber/30"
          : "bg-studio-900 border-studio-700/60 hover:border-studio-600 hover:bg-studio-850/80 shadow-studio-card"
      }`}
    >
      {/* Card Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 rounded-md bg-studio-800 border border-studio-700 flex items-center justify-center font-mono text-xs font-medium text-studio-200 shadow-sm">
            #{index + 1}
          </span>
          <span className="text-xs font-mono px-2 py-0.5 rounded-md bg-studio-950 border border-studio-800 text-studio-300 tabular-nums">
            {duration}s
          </span>
          {clip.needs_easter_egg_zoom && (
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-tally-amber/10 border border-tally-amber/30 text-tally-amber font-medium">
              Zoom detail
            </span>
          )}
        </div>

        {/* Overall Virality Score */}
        <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-md border text-xs font-mono font-medium tabular-nums ${
          overallScore >= 85
            ? "bg-tally-amber/10 border-tally-amber/40 text-tally-amber shadow-sm"
            : "bg-studio-950 border-studio-800 text-studio-100"
        }`}>
          <span className={`w-1.5 h-1.5 rounded-full ${overallScore >= 85 ? "bg-tally-amber animate-pulse" : "bg-studio-500"}`} />
          <span>{overallScore}</span>
          <span className="text-[10px] text-studio-500">/100</span>
        </div>
      </div>

      {/* Title Hook */}
      <h3 className="font-medium text-studio-100 text-sm leading-snug line-clamp-2 group-hover:text-white transition-colors">
        {clip.title_hook}
      </h3>

      {/* 4-Vector Virality Scorecard Bars */}
      <div className="grid grid-cols-2 gap-2.5 text-[10px] font-mono text-studio-400 pt-1">
        <div>
          <div className="flex justify-between mb-1">
            <span>Visual hook</span>
            <span className="text-studio-200 tabular-nums">{v?.three_second_visual_hook ?? 0}%</span>
          </div>
          <div className="h-1 bg-studio-950 rounded-full overflow-hidden border border-studio-800/60">
            <div
              className="h-full bg-tally-amber transition-all duration-300"
              style={{ width: `${v?.three_second_visual_hook ?? 0}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between mb-1">
            <span>Replay loop</span>
            <span className="text-studio-200 tabular-nums">{v?.replay_loop_factor ?? 0}%</span>
          </div>
          <div className="h-1 bg-studio-950 rounded-full overflow-hidden border border-studio-800/60">
            <div
              className="h-full bg-tally-emerald transition-all duration-300"
              style={{ width: `${v?.replay_loop_factor ?? 0}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between mb-1">
            <span>Debate bait</span>
            <span className="text-studio-200 tabular-nums">
              {v?.debate_comment_bait_potential ?? 0}%
            </span>
          </div>
          <div className="h-1 bg-studio-950 rounded-full overflow-hidden border border-studio-800/60">
            <div
              className="h-full bg-sky-400 transition-all duration-300"
              style={{ width: `${v?.debate_comment_bait_potential ?? 0}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between mb-1">
            <span>Payoff speed</span>
            <span className="text-studio-200 tabular-nums">{v?.payoff_speed ?? 0}%</span>
          </div>
          <div className="h-1 bg-studio-950 rounded-full overflow-hidden border border-studio-800/60">
            <div
              className="h-full bg-indigo-400 transition-all duration-300"
              style={{ width: `${v?.payoff_speed ?? 0}%` }}
            />
          </div>
        </div>
      </div>

      {/* Action Footer */}
      <div className="pt-2 border-t border-studio-800 flex items-center justify-between gap-2">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onOpenUploadKit();
          }}
          className="px-2.5 py-1.5 rounded-md bg-studio-800 hover:bg-studio-750 border border-studio-700 text-studio-300 hover:text-white text-xs font-mono transition-colors flex items-center gap-1.5 btn-tactile shadow-sm"
          title="Open upload kit metadata & cover prompt"
        >
          <FileText className="w-3.5 h-3.5 text-studio-400" />
          <span>Upload kit</span>
        </button>

        <button
          onClick={(e) => {
            e.stopPropagation();
            onRender();
          }}
          disabled={isRendering}
          className={`px-3 py-1.5 rounded-md text-xs font-mono font-medium transition-all flex items-center gap-1.5 btn-tactile ${
            isCompleted
              ? "bg-studio-800 border border-tally-emerald/40 text-tally-emerald"
              : isRendering
              ? "bg-studio-800 text-studio-400 cursor-wait border border-studio-700"
              : "bg-tally-amber hover:bg-amber-400 text-studio-950 shadow-studio-raised font-semibold"
          }`}
        >
          {isRendering ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>Rendering...</span>
            </>
          ) : isCompleted ? (
            <>
              <CheckCircle className="w-3.5 h-3.5" />
              <span>Re-export</span>
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Render short</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
