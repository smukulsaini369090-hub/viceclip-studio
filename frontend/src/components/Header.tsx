"use client";

import React from "react";
import { Cpu, HardDrive, ListVideo, Settings, Sparkles, FolderOpen } from "lucide-react";
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
}

export const Header: React.FC<HeaderProps> = ({
  systemStatus,
  vramUsedMb,
  vramTotalMb,
  onOpenSettings,
  onOpenBatchQueue,
  onOpenRetentionVault,
  onOpenCache,
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
    <header className="sticky top-0 z-40 bg-[#0A0A0F]/90 backdrop-blur-md border-b border-[#262636] px-4 py-2.5 flex items-center justify-between">
      {/* Brand Identity */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded bg-gradient-to-br from-[#FF2E93] to-[#00F0FF] flex items-center justify-center font-bold text-black text-sm tracking-wider shadow-neon-pink">
          VC
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-bold tracking-tight text-white text-base">VICECLIP STUDIO</h1>
            <span className="text-[10px] font-mono tracking-wider px-1.5 py-0.5 rounded bg-[#1A1A24] text-[#00F0FF] border border-[#00F0FF]/30">
              GTA 6 EDITION
            </span>
          </div>
          <p className="text-[11px] text-[#7E7E9A]">Local-First AI Viral Video Pipeline</p>
        </div>
      </div>

      {/* Hardware Telemetry Strip */}
      <div className="hidden lg:flex items-center gap-4 bg-[#121218] border border-[#262636] px-3 py-1.5 rounded-lg text-xs">
        {/* Encoder Pill */}
        <div className="flex items-center gap-1.5">
          <Cpu className={`w-3.5 h-3.5 ${isNvenc ? "text-[#00F0FF]" : "text-[#FFE600]"}`} />
          <span className="text-[#7E7E9A]">ENCODER:</span>
          <span className={`font-mono font-medium ${isNvenc ? "text-[#00F0FF]" : "text-[#FFE600]"}`}>
            {isNvenc ? "h264_nvenc (RTX 3050)" : "libx264 (CPU)"}
          </span>
        </div>

        <div className="h-3 w-[1px] bg-[#262636]" />

        {/* VRAM Meter */}
        <div className="flex items-center gap-2">
          <HardDrive className="w-3.5 h-3.5 text-[#FF2E93]" />
          <span className="text-[#7E7E9A]">VRAM:</span>
          <span className="font-mono tabular-nums text-white">
            {vramUsedMb} <span className="text-[#7E7E9A]">/ {vramTotalMb} MB</span>
          </span>
          <div className="w-16 h-2 bg-[#1A1A24] rounded-full overflow-hidden border border-[#262636]">
            <div
              className="h-full bg-gradient-to-r from-[#00F0FF] via-[#FF2E93] to-[#FFE600] transition-all duration-300"
              style={{ width: `${Math.min(100, vramPct)}%` }}
            />
          </div>
          <span className="font-mono tabular-nums text-[11px] text-[#7E7E9A]">
            {vramPct}%
          </span>
        </div>
      </div>

      {/* Action Controls */}
      <div className="flex items-center gap-2">
        <button
          onClick={handleOpenExplorer}
          className="p-2 rounded-lg bg-[#121218] hover:bg-[#1A1A24] border border-[#262636] text-[#E2E2F0] hover:text-[#00F0FF] transition-colors text-xs flex items-center gap-1.5"
          title="Open Output Folder in Windows Explorer"
        >
          <FolderOpen className="w-4 h-4" />
          <span className="hidden sm:inline">Outputs</span>
        </button>

        <button
          onClick={onOpenCache}
          className="p-2 rounded-lg bg-[#121218] hover:bg-[#1A1A24] border border-[#262636] text-[#E2E2F0] hover:text-[#00F0FF] transition-colors text-xs flex items-center gap-1.5"
          title="SQLite Smart Cache Library"
        >
          <HardDrive className="w-4 h-4" />
          <span className="hidden sm:inline">Cache</span>
        </button>

        <button
          onClick={onOpenBatchQueue}
          className="p-2 rounded-lg bg-[#121218] hover:bg-[#1A1A24] border border-[#262636] text-[#E2E2F0] hover:text-[#FF2E93] transition-colors text-xs flex items-center gap-1.5"
          title="Batch Watchlist Queue"
        >
          <ListVideo className="w-4 h-4" />
          <span className="hidden sm:inline">Batch Queue</span>
        </button>

        <button
          onClick={onOpenRetentionVault}
          className="p-2 rounded-lg bg-[#121218] hover:bg-[#1A1A24] border border-[#262636] text-[#E2E2F0] hover:text-[#FFE600] transition-colors text-xs flex items-center gap-1.5"
          title="Self-Learning Retention Vault"
        >
          <Sparkles className="w-4 h-4" />
          <span className="hidden sm:inline">Retention Vault</span>
        </button>

        <button
          onClick={onOpenSettings}
          className="p-2 rounded-lg bg-[#121218] hover:bg-[#1A1A24] border border-[#262636] text-[#E2E2F0] hover:text-white transition-colors"
          title="Settings & Hardware Diagnostics"
        >
          <Settings className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
