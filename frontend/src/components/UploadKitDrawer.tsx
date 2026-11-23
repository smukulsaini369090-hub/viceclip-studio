"use client";

import React, { useState } from "react";
import {
  X,
  Copy,
  Check,
  FolderOpen,
  Image as ImageIcon,
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
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-[#121218] border-l border-[#262636] shadow-2xl flex flex-col p-5 overflow-y-auto">
      {/* Drawer Header */}
      <div className="flex items-center justify-between pb-4 border-b border-[#262636]">
        <div>
          <h3 className="font-bold text-white text-sm tracking-tight flex items-center gap-2">
            <span>1-CLICK UPLOAD KIT</span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#00F0FF]/10 text-[#00F0FF] border border-[#00F0FF]/30">
              {clip.clip_id}
            </span>
          </h3>
          <p className="text-xs text-[#7E7E9A]">Optimized for YouTube Shorts monetization</p>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg bg-[#1A1A24] text-[#7E7E9A] hover:text-white"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="py-4 space-y-5 flex-1">
        {/* Viral Title Options */}
        <div className="space-y-2">
          <div className="text-xs font-mono text-[#00F0FF] flex items-center gap-1.5">
            <Type className="w-3.5 h-3.5" />
            <span>3 VIRAL TITLE OPTIONS:</span>
          </div>
          {titles.map((title, idx) => (
            <div
              key={idx}
              className="p-2.5 rounded-lg bg-[#0A0A0F] border border-[#262636] flex items-center justify-between gap-2 group"
            >
              <span className="text-xs text-white line-clamp-2">{title}</span>
              <button
                onClick={() => copyToClipboard(title, `title-${idx}`)}
                className="p-1.5 rounded bg-[#1A1A24] hover:bg-[#262636] text-[#00F0FF] shrink-0"
                title="Copy Title"
              >
                {copiedKey === `title-${idx}` ? (
                  <Check className="w-3.5 h-3.5 text-green-400" />
                ) : (
                  <Copy className="w-3.5 h-3.5" />
                )}
              </button>
            </div>
          ))}
        </div>

        {/* Targeted GTA 6 Hashtags */}
        <div className="space-y-2">
          <div className="text-xs font-mono text-[#FF2E93] flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <Hash className="w-3.5 h-3.5" />
              <span>TARGETED HASHTAGS:</span>
            </span>
            <button
              onClick={() => copyToClipboard(hashtags, "hashtags")}
              className="text-[11px] text-[#FF2E93] hover:underline flex items-center gap-1 font-mono"
            >
              {copiedKey === "hashtags" ? (
                <>
                  <Check className="w-3 h-3 text-green-400" />
                  <span>COPIED</span>
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3" />
                  <span>COPY ALL</span>
                </>
              )}
            </button>
          </div>
          <div className="p-2.5 rounded-lg bg-[#0A0A0F] border border-[#262636] text-xs font-mono text-[#E2E2F0]">
            {hashtags}
          </div>
        </div>

        {/* Debate-Sparking Pinned Comment */}
        <div className="space-y-2">
          <div className="text-xs font-mono text-[#FFE600] flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <MessageSquare className="w-3.5 h-3.5" />
              <span>DEBATE PINNED COMMENT:</span>
            </span>
            <button
              onClick={() => copyToClipboard(pinnedComment, "comment")}
              className="text-[11px] text-[#FFE600] hover:underline flex items-center gap-1 font-mono"
            >
              {copiedKey === "comment" ? (
                <>
                  <Check className="w-3 h-3 text-green-400" />
                  <span>COPIED</span>
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3" />
                  <span>COPY</span>
                </>
              )}
            </button>
          </div>
          <div className="p-2.5 rounded-lg bg-[#0A0A0F] border border-[#262636] text-xs text-[#E2E2F0] italic">
            "{pinnedComment}"
          </div>
        </div>

        {/* Output Explorer Actions */}
        <div className="pt-2">
          <button
            onClick={handleOpenFolder}
            className="w-full py-2.5 bg-[#1A1A24] hover:bg-[#262636] border border-[#262636] text-[#00F0FF] rounded-lg text-xs font-mono font-bold flex items-center justify-center gap-2 transition-colors"
          >
            <FolderOpen className="w-4 h-4" />
            <span>OPEN OUTPUT IN WINDOWS EXPLORER</span>
          </button>
        </div>
      </div>
    </div>
  );
};
