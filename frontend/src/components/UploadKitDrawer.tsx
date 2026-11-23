"use client";

import React, { useState } from "react";
import {
  X,
  Copy,
  Check,
  FolderOpen,
  MessageSquare,
  Hash,
  Type,
} from "lucide-react";
import { ClipCandidate } from "@/types";
import { openOutputFolder } from "@/lib/api";

interface UploadKitDrawerProps {
  clip: ClipCandidate | null;
  videoId: string | null;
  onClose: () => void;
}

export const UploadKitDrawer: React.FC<UploadKitDrawerProps> = ({
  clip,
  videoId,
  onClose,
}) => {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  if (!clip) return null;

  const kit = clip.upload_kit;
  const titles = kit?.titles || [clip.title_hook];
  const hashtags = kit?.hashtags?.join(" ") || "#GTA6 #Shorts #GrandTheftAuto6";
  const pinnedComment = kit?.pinned_comment || "Did anyone else catch this secret detail in GTA 6?";

  const copyToClipboard = async (text: string, key: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedKey(key);
      setTimeout(() => setCopiedKey(null), 1800);
    } catch (err) {
      console.error("Failed to copy", err);
    }
  };

  const handleOpenFolder = async () => {
    try {
      await openOutputFolder(videoId || undefined, clip.clip_id);
    } catch (err) {
      console.error("Failed to open explorer", err);
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-studio-900 border-l border-studio-700/80 shadow-2xl flex flex-col p-5 overflow-y-auto">
      {/* Drawer Header */}
      <div className="flex items-center justify-between pb-4 border-b border-studio-800">
        <div>
          <h3 className="font-medium text-studio-100 text-sm tracking-tight flex items-center gap-2">
            <span>Upload kit</span>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-studio-800 text-studio-300 border border-studio-700">
              {clip.clip_id}
            </span>
          </h3>
          <p className="text-xs text-studio-400 mt-0.5">Optimized for YouTube Shorts distribution</p>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded bg-studio-800 hover:bg-studio-700 text-studio-400 hover:text-white transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="py-4 space-y-5 flex-1">
        {/* Viral Title Options */}
        <div className="space-y-2">
          <div className="text-xs font-mono text-studio-300 flex items-center gap-1.5 font-medium">
            <Type className="w-3.5 h-3.5 text-studio-400" />
            <span>Headline variants</span>
          </div>
          {titles.map((title, idx) => (
            <div
              key={idx}
              className="p-3 rounded bg-studio-950 border border-studio-800 flex items-center justify-between gap-2 group"
            >
              <span className="text-xs text-studio-200 line-clamp-2 leading-relaxed">{title}</span>
              <button
                onClick={() => copyToClipboard(title, `title-${idx}`)}
                className="p-1.5 rounded bg-studio-850 hover:bg-studio-800 border border-studio-800 text-studio-400 hover:text-studio-200 shrink-0 transition-colors"
                title="Copy title"
              >
                {copiedKey === `title-${idx}` ? (
                  <Check className="w-3.5 h-3.5 text-tally-emerald" />
                ) : (
                  <Copy className="w-3.5 h-3.5" />
                )}
              </button>
            </div>
          ))}
        </div>

        {/* Targeted GTA 6 Hashtags */}
        <div className="space-y-2">
          <div className="text-xs font-mono text-studio-300 flex items-center justify-between font-medium">
            <span className="flex items-center gap-1.5">
              <Hash className="w-3.5 h-3.5 text-studio-400" />
              <span>Targeted hashtags</span>
            </span>
            <button
              onClick={() => copyToClipboard(hashtags, "hashtags")}
              className="text-[11px] text-studio-400 hover:text-studio-200 flex items-center gap-1 font-mono transition-colors"
            >
              {copiedKey === "hashtags" ? (
                <>
                  <Check className="w-3 h-3 text-tally-emerald" />
                  <span>Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3" />
                  <span>Copy all</span>
                </>
              )}
            </button>
          </div>
          <div className="p-3 rounded bg-studio-950 border border-studio-800 text-xs font-mono text-studio-300 leading-relaxed">
            {hashtags}
          </div>
        </div>

        {/* Debate-Sparking Pinned Comment */}
        <div className="space-y-2">
          <div className="text-xs font-mono text-studio-300 flex items-center justify-between font-medium">
            <span className="flex items-center gap-1.5">
              <MessageSquare className="w-3.5 h-3.5 text-studio-400" />
              <span>Pinned comment hook</span>
            </span>
            <button
              onClick={() => copyToClipboard(pinnedComment, "comment")}
              className="text-[11px] text-studio-400 hover:text-studio-200 flex items-center gap-1 font-mono transition-colors"
            >
              {copiedKey === "comment" ? (
                <>
                  <Check className="w-3 h-3 text-tally-emerald" />
                  <span>Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3" />
                  <span>Copy</span>
                </>
              )}
            </button>
          </div>
          <div className="p-3 rounded bg-studio-950 border border-studio-800 text-xs text-studio-300 italic leading-relaxed">
            "{pinnedComment}"
          </div>
        </div>

        {/* Output Explorer Actions */}
        <div className="pt-2">
          <button
            onClick={handleOpenFolder}
            className="w-full py-2.5 bg-studio-800 hover:bg-studio-750 border border-studio-700 text-studio-200 hover:text-white rounded text-xs font-mono font-medium flex items-center justify-center gap-2 transition-colors"
          >
            <FolderOpen className="w-4 h-4 text-studio-400" />
            <span>Open output folder</span>
          </button>
        </div>
      </div>
    </div>
  );
};
