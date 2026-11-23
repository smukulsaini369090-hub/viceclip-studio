"use client";

import React, { useEffect, useState } from "react";
import { X, HardDrive, Trash2, Clock, Play, Loader2 } from "lucide-react";
import { CachedVideo } from "@/types";
import { deleteCachedVideo, listCache } from "@/lib/api";

interface SmartCacheSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectVideo: (videoId: string) => void;
}

export const SmartCacheSidebar: React.FC<SmartCacheSidebarProps> = ({
  isOpen,
  onClose,
  onSelectVideo,
}) => {
  const [cachedVideos, setCachedVideos] = useState<CachedVideo[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchCache = async () => {
    setIsLoading(true);
    try {
      const res = await listCache();
      setCachedVideos(res.videos);
    } catch (err) {
      console.error("Failed to list cache", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchCache();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleDelete = async (e: React.MouseEvent, videoId: string) => {
    e.stopPropagation();
    try {
      await deleteCachedVideo(videoId);
      await fetchCache();
    } catch (err) {
      console.error("Failed to delete cached video", err);
    }
  };

  const formatSec = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${sec.toString().padStart(2, "0")}`;
  };

  return (
    <div className="fixed inset-y-0 left-0 z-50 w-full max-w-sm bg-[#121218] border-r border-[#262636] shadow-2xl flex flex-col p-5 overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-[#262636]">
        <div>
          <h3 className="font-bold text-white text-sm tracking-tight flex items-center gap-2">
            <HardDrive className="w-4 h-4 text-[#00F0FF]" />
            <span>SQLITE SMART CACHE</span>
          </h3>
          <p className="text-xs text-[#7E7E9A]">Zero-wait instant reload library</p>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg bg-[#1A1A24] text-[#7E7E9A] hover:text-white"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Videos List */}
      <div className="py-4 space-y-3 flex-1">
        {isLoading && (
          <div className="flex items-center justify-center p-6 text-xs font-mono text-[#7E7E9A] gap-2">
            <Loader2 className="w-4 h-4 animate-spin text-[#00F0FF]" />
            <span>Loading cache...</span>
          </div>
        )}

        {!isLoading && cachedVideos.length === 0 && (
          <div className="p-6 text-center text-xs font-mono text-[#505068] border border-dashed border-[#262636] rounded-lg">
            Smart Cache is empty. Analyzed videos will automatically appear here for instant reload.
          </div>
        )}

        {cachedVideos.map((v) => (
          <div
            key={v.video_id}
            onClick={() => {
              onSelectVideo(v.video_id);
              onClose();
            }}
            className="p-3 bg-[#0A0A0F] hover:bg-[#161620] border border-[#262636] hover:border-[#00F0FF]/40 rounded-xl cursor-pointer transition-all flex flex-col gap-2 group"
          >
            <div className="flex items-start justify-between gap-2">
              <h4 className="text-xs font-bold text-white line-clamp-2 group-hover:text-[#00F0FF] transition-colors">
                {v.title || v.video_id}
              </h4>
              <button
                onClick={(e) => handleDelete(e, v.video_id)}
                className="p-1 text-[#505068] hover:text-red-400 shrink-0"
                title="Delete from cache"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="flex items-center justify-between text-[11px] font-mono text-[#7E7E9A]">
              <span className="truncate max-w-[150px]">{v.channel}</span>
              <span className="tabular-nums flex items-center gap-1">
                <Clock className="w-3 h-3" /> {formatSec(v.duration_sec)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
