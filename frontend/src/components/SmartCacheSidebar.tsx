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
    <div className="fixed inset-y-0 left-0 z-50 w-full max-w-sm bg-studio-900 border-r border-studio-700/80 shadow-2xl flex flex-col p-5 overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-studio-800">
        <div>
          <h3 className="font-medium text-studio-100 text-sm tracking-tight flex items-center gap-2">
            <HardDrive className="w-4 h-4 text-studio-400" />
            <span>Smart cache library</span>
          </h3>
          <p className="text-xs text-studio-400 mt-0.5">Instant zero-wait reload history</p>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded bg-studio-800 hover:bg-studio-700 text-studio-400 hover:text-white transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Videos List */}
      <div className="py-4 space-y-3 flex-1">
        {isLoading && (
          <div className="flex items-center justify-center p-6 text-xs font-mono text-studio-400 gap-2">
            <Loader2 className="w-4 h-4 animate-spin text-tally-amber" />
            <span>Loading cache...</span>
          </div>
        )}

        {!isLoading && cachedVideos.length === 0 && (
          <div className="p-6 text-center text-xs font-mono text-studio-500 border border-dashed border-studio-800 rounded">
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
            className="p-3 bg-studio-950 hover:bg-studio-850 border border-studio-800 hover:border-studio-700 rounded cursor-pointer transition-colors flex flex-col gap-2 group"
          >
            <div className="flex items-start justify-between gap-2">
              <h4 className="text-xs font-medium text-studio-200 line-clamp-2 group-hover:text-white transition-colors">
                {v.title || v.video_id}
              </h4>
              <button
                onClick={(e) => handleDelete(e, v.video_id)}
                className="p-1 text-studio-500 hover:text-tally-red shrink-0 transition-colors"
                title="Delete from cache"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="flex items-center justify-between text-[11px] font-mono text-studio-400">
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
