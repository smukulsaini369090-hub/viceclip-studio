"use client";

import React, { useState } from "react";
import { HardDrive, Activity, Terminal, ChevronUp, ChevronDown } from "lucide-react";
import { PipelineTelemetry } from "@/types";

interface TelemetryBarProps {
  telemetry: PipelineTelemetry;
}

export const TelemetryBar: React.FC<TelemetryBarProps> = ({ telemetry }) => {
  const [isConsoleOpen, setIsConsoleOpen] = useState(false);

  const vramUsed = telemetry.vram_used_mb || 0;
  const vramTotal = telemetry.vram_total_mb || 6144;
  const vramPct = Math.round((vramUsed / vramTotal) * 100);

  const isBusy = telemetry.stage !== "idle" && telemetry.stage !== "complete";

  return (
    <div className="fixed bottom-0 left-0 right-0 z-40 bg-[#0A0A0F]/95 backdrop-blur-md border-t border-[#262636]">
      {/* Console Drawer */}
      {isConsoleOpen && (
        <div className="p-3 bg-[#07070A] border-b border-[#262636] max-h-40 overflow-y-auto text-xs font-mono text-[#7E7E9A] space-y-1">
          <div className="flex items-center justify-between text-[11px] text-[#505068] mb-1">
            <span>REAL-TIME PIPELINE LOG STREAM:</span>
            <span>STAGE: {telemetry.stage}</span>
          </div>
          <div className="text-white flex items-center gap-2">
            <span className="text-[#00F0FF]">▶</span>
            <span>{telemetry.log_message || "Awaiting task..."}</span>
          </div>
        </div>
      )}

      {/* Main Bar */}
      <div className="px-4 py-2 flex items-center justify-between gap-4 text-xs font-mono">
        {/* Stage & Progress Indicator */}
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <div className="flex items-center gap-2 shrink-0">
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                isBusy
                  ? "bg-[#00F0FF] animate-ping"
                  : telemetry.stage === "complete"
                  ? "bg-green-400"
                  : "bg-[#505068]"
              }`}
            />
            <span className="font-bold text-white truncate max-w-[180px] sm:max-w-none">
              {telemetry.stage_label || "SYSTEM IDLE"}
            </span>
          </div>

          {/* Progress Bar */}
          <div className="flex-1 max-w-md h-2 bg-[#1A1A24] rounded-full overflow-hidden border border-[#262636] hidden sm:block">
            <div
              className="h-full bg-gradient-to-r from-[#FF2E93] to-[#00F0FF] transition-all duration-300"
              style={{ width: `${Math.min(100, telemetry.progress_pct || 0)}%` }}
            />
          </div>
          <span className="text-[#00F0FF] tabular-nums font-bold shrink-0 hidden sm:inline">
            {Math.round(telemetry.progress_pct || 0)}%
          </span>
        </div>

        {/* Live RTX 3050 VRAM Gauge */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="flex items-center gap-2">
            <HardDrive className="w-3.5 h-3.5 text-[#FF2E93]" />
            <span className="text-[#7E7E9A] hidden md:inline">RTX 3050 VRAM:</span>
            <span className="text-white tabular-nums">
              {vramUsed} <span className="text-[#7E7E9A]">/ {vramTotal} MB</span>
            </span>
            <span
              className={`px-1.5 py-0.2 rounded text-[10px] tabular-nums font-bold ${
                vramPct > 85 ? "bg-red-500/20 text-red-400" : "bg-[#1A1A24] text-[#00F0FF]"
              }`}
            >
              {vramPct}%
            </span>
          </div>

          {/* Console Toggle */}
          <button
            onClick={() => setIsConsoleOpen(!isConsoleOpen)}
            className="p-1 rounded bg-[#1A1A24] hover:bg-[#262636] text-[#7E7E9A] hover:text-white transition-colors"
            title="Toggle Console Log Stream"
          >
            {isConsoleOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </div>
  );
};
