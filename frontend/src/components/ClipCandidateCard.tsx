"use client";

import React from "react";
import { Play, Sparkles, FolderOpen, Layers, CheckCircle, Loader2 } from "lucide-react";
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
      className={`p-4 rounded-xl border transition-all cursor-pointer flex flex-col gap-3 ${
        isActive
          ? "bg-[#161620] border-[#00F0FF] shadow-neon-cyan"
          : "bg-[#121218] border-[#262636] hover:border-[#3A3A52]"
      }`}
    >
      {/* Card Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 rounded bg-[#1A1A24] border border-[#262636] flex items-center justify-center font-mono font-bold text-xs text-[#00F0FF]">
            #{index + 1}
          </span>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-[#0A0A0F] border border-[#262636] text-[#7E7E9A] tabular-nums">
            {duration}s
          </span>
          {clip.needs_easter_egg_zoom && (
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#FFE600]/10 border border-[#FFE600]/40 text-[#FFE600]">
              EASTER EGG
            </span>
          )}
        </div>

        {/* Overall Virality Score */}
        <div className="flex items-center gap-1.5 bg-[#0A0A0F] border border-[#262636] px-2.5 py-1 rounded-lg">
          <Sparkles className="w-3.5 h-3.5 text-[#FF2E93]" />
          <span className="text-xs font-mono font-bold text-white tabular-nums">
            {overallScore}
          </span>
          <span className="text-[10px] text-[#7E7E9A]">/100</span>
        </div>
      </div>

      {/* Title Hook */}
      <h3 className="font-bold text-white text-sm line-clamp-2">{clip.title_hook}</h3>

      {/* 4-Vector Virality Scorecard Bars */}
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-[#7E7E9A] pt-1">
        <div>
          <div className="flex justify-between mb-0.5">
            <span>VISUAL HOOK</span>
            <span className="text-white tabular-nums">{v?.three_second_visual_hook ?? 0}%</span>
          </div>
          <div className="h-1 bg-[#1A1A24] rounded-full overflow-hidden">
            <div
              className="h-full bg-[#FF2E93]"
              style={{ width: `${v?.three_second_visual_hook ?? 0}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between mb-0.5">
            <span>REPLAY LOOP</span>
            <span className="text-white tabular-nums">{v?.replay_loop_factor ?? 0}%</span>
          </div>
          <div className="h-1 bg-[#1A1A24] rounded-full overflow-hidden">
            <div
              className="h-full bg-[#00F0FF]"
              style={{ width: `${v?.replay_loop_factor ?? 0}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between mb-0.5">
            <span>DEBATE BAIT</span>
            <span className="text-white tabular-nums">
              {v?.debate_comment_bait_potential ?? 0}%
            </span>
          </div>
          <div className="h-1 bg-[#1A1A24] rounded-full overflow-hidden">
            <div
              className="h-full bg-[#FFE600]"
              style={{ width: `${v?.debate_comment_bait_potential ?? 0}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between mb-0.5">
            <span>PAYOFF SPEED</span>
            <span className="text-white tabular-nums">{v?.payoff_speed ?? 0}%</span>
          </div>
          <div className="h-1 bg-[#1A1A24] rounded-full overflow-hidden">
            <div
              className="h-full bg-[#9D00FF]"
              style={{ width: `${v?.payoff_speed ?? 0}%` }}
            />
          </div>
        </div>
      </div>

      {/* Action Footer */}
      <div className="pt-2 border-t border-[#1E1E2A] flex items-center justify-between gap-2">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onOpenUploadKit();
          }}
          className="px-2.5 py-1.5 rounded-lg bg-[#0A0A0F] hover:bg-[#1A1A24] border border-[#262636] text-[#7E7E9A] hover:text-[#00F0FF] text-xs font-mono transition-colors flex items-center gap-1.5"
          title="Open Upload Kit metadata & cover image"
        >
          <Layers className="w-3.5 h-3.5" />
          <span>Upload Kit</span>
        </button>

        <button
          onClick={(e) => {
            e.stopPropagation();
            onRender();
          }}
          disabled={isRendering}
          className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all flex items-center gap-1.5 ${
            isCompleted
              ? "bg-green-500/15 border border-green-500 text-green-400"
              : isRendering
              ? "bg-[#1A1A24] text-[#7E7E9A] cursor-wait"
              : "bg-gradient-to-r from-[#FF2E93] to-[#00F0FF] text-black hover:opacity-90 shadow-neon-pink"
          }`}
        >
          {isRendering ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>RENDERING...</span>
            </>
          ) : isCompleted ? (
            <>
              <CheckCircle className="w-3.5 h-3.5" />
              <span>RE-EXPORT</span>
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>RENDER SHORT</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
