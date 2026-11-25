"use client";

import React from "react";
import { Cpu, HardDrive, ListVideo, Settings, Sparkles, FolderOpen, Keyboard } from "lucide-react";
import { SystemStatus } from "@/types";
import { openOutputFolder } from "@/lib/api";

interface HeaderProps {
  systemStatus: SystemStatus | null;
  vramUsedMb: number;
  vramTotalMb: number;
  onOpenSettings: () => void;
  onOpenBatchQueue: () => void;
  onOpenRetentionVault: () => void;
  onOpenCache: () => void;
  onOpenShortcuts?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  systemStatus,
  vramUsedMb,
  vramTotalMb,
  onOpenSettings,
  onOpenBatchQueue,
  onOpenRetentionVault,
  onOpenCache,
  onOpenShortcuts,
}) => {
  const vramPct = vramTotalMb > 0 ? Math.round((vramUsedMb / vramTotalMb) * 100) : 0;
  const isNvenc = systemStatus?.encoder === "h264_nvenc";

  const handleOpenExplorer = async () => {
    try {
      await openOutputFolder();
    } catch (err) {
      console.error("Failed to open explorer", err);
    }
  };

  return (
    <header className="sticky top-0 z-40 bg-studio-900/95 backdrop-blur-md border-b border-studio-600 px-4 py-2.5 flex items-center justify-between">
      {/* Brand Identity */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-studio-700 border border-studio-600 flex items-center justify-center font-mono font-bold text-studio-100 text-xs shadow-studio-card relative">
          <span>VC</span>
          <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-tally-amber animate-pulse shadow-sm" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-medium tracking-tight text-studio-100 text-sm">ViceClip Studio</h1>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-studio-700 text-studio-300 border border-studio-600">
              GTA 6
            </span>
          </div>
          <p className="text-[11px] text-studio-400">Local-first AI clipping workstation</p>
        </div>
      </div>

      {/* Hardware Telemetry Strip */}
      <div className="hidden lg:flex items-center gap-3.5 bg-studio-800 border border-studio-600 px-3 py-1.5 rounded-lg text-xs shadow-studio-card">
        {/* Encoder Pill */}
        <div className="flex items-center gap-1.5 font-mono text-[11px]">
          <span className={`w-1.5 h-1.5 rounded-full ${isNvenc ? "bg-tally-emerald" : "bg-tally-amber"}`} />
          <span className="text-studio-400">Encoder:</span>
          <span className="text-studio-200 font-medium">
            {isNvenc ? "NVENC (RTX 3050)" : "x264 (CPU)"}
          </span>
        </div>

        <div className="h-3 w-[1px] bg-studio-600" />

        {/* VRAM Meter */}
        <div className="flex items-center gap-2 font-mono text-[11px]">
          <span className="text-studio-400">VRAM:</span>
          <span className="tabular-nums text-studio-200">
            {vramUsedMb} <span className="text-studio-400">/ {vramTotalMb} MB</span>
          </span>
          <div className="w-14 h-1.5 bg-studio-950 rounded-full overflow-hidden border border-studio-600">
            <div
              className="h-full bg-tally-amber transition-all duration-300"
              style={{ width: `${Math.min(100, vramPct)}%` }}
            />
          </div>
          <span className="tabular-nums text-[10px] text-studio-400">
            {vramPct}%
          </span>
        </div>
      </div>

      {/* Action Controls */}
      <div className="flex items-center gap-1.5">
        <button
          onClick={handleOpenExplorer}
          className="px-2.5 py-1.5 rounded-lg bg-studio-800 hover:bg-studio-700 border border-studio-600 text-studio-300 hover:text-studio-100 transition-all text-xs flex items-center gap-1.5 shadow-studio-card btn-tactile"
          title="Open Output Folder in Windows Explorer"
        >
          <FolderOpen className="w-3.5 h-3.5 text-studio-400" />
          <span className="hidden sm:inline">Outputs</span>
        </button>

        <button
          onClick={onOpenCache}
          className="px-2.5 py-1.5 rounded-lg bg-studio-800 hover:bg-studio-700 border border-studio-600 text-studio-300 hover:text-studio-100 transition-all text-xs flex items-center gap-1.5 shadow-studio-card btn-tactile"
          title="SQLite Smart Cache Library"
        >
          <HardDrive className="w-3.5 h-3.5 text-studio-400" />
          <span className="hidden sm:inline">Cache</span>
        </button>

        <button
          onClick={onOpenBatchQueue}
          className="px-2.5 py-1.5 rounded-lg bg-studio-800 hover:bg-studio-700 border border-studio-600 text-studio-300 hover:text-studio-100 transition-all text-xs flex items-center gap-1.5 shadow-studio-card btn-tactile"
          title="Batch Watchlist Queue"
        >
          <ListVideo className="w-3.5 h-3.5 text-studio-400" />
          <span className="hidden sm:inline">Batch Queue</span>
        </button>

        <button
          onClick={onOpenRetentionVault}
          className="px-2.5 py-1.5 rounded-lg bg-studio-800 hover:bg-studio-700 border border-studio-600 text-studio-300 hover:text-studio-100 transition-all text-xs flex items-center gap-1.5 shadow-studio-card btn-tactile"
          title="Self-Learning Retention Vault"
        >
          <Sparkles className="w-3.5 h-3.5 text-studio-400" />
          <span className="hidden sm:inline">Vault</span>
        </button>

        {onOpenShortcuts && (
          <button
            onClick={onOpenShortcuts}
            className="p-1.5 rounded-lg bg-studio-800 hover:bg-studio-700 border border-studio-600 text-studio-400 hover:text-studio-100 transition-all shadow-studio-card btn-tactile"
            title="Keyboard Shortcuts (?)"
          >
            <Keyboard className="w-4 h-4" />
          </button>
        )}

        <button
          onClick={onOpenSettings}
          className="p-1.5 rounded-lg bg-studio-800 hover:bg-studio-700 border border-studio-600 text-studio-400 hover:text-studio-100 transition-all shadow-studio-card btn-tactile"
          title="Settings & Hardware Diagnostics"
        >
          <Settings className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
