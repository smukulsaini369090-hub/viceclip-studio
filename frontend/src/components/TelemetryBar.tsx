"use client";

import React, { useState } from "react";
import { HardDrive, ChevronUp, ChevronDown } from "lucide-react";
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
    <div className="fixed bottom-0 left-0 right-0 z-40 bg-studio-950/95 backdrop-blur-md border-t border-studio-800">
      {/* Console Drawer */}
      {isConsoleOpen && (
        <div className="p-3 bg-studio-950 border-b border-studio-800 max-h-40 overflow-y-auto text-xs font-mono text-studio-400 space-y-1">
          <div className="flex items-center justify-between text-[11px] text-studio-500 mb-1">
            <span>Pipeline log stream:</span>
            <span>Stage: {telemetry.stage}</span>
          </div>
          <div className="text-studio-200 flex items-center gap-2">
            <span className="text-tally-amber">▶</span>
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
              className={`w-2 h-2 rounded-full ${
                isBusy
                  ? "bg-tally-amber animate-pulse"
                  : telemetry.stage === "complete"
                  ? "bg-tally-emerald"
                  : "bg-studio-600"
              }`}
            />
            <span className="font-medium text-studio-100 truncate max-w-[180px] sm:max-w-none">
              {telemetry.stage_label || "System idle"}
            </span>
          </div>

          {/* Progress Bar */}
          <div className="flex-1 max-w-md h-1.5 bg-studio-900 rounded overflow-hidden border border-studio-800 hidden sm:block">
            <div
              className="h-full bg-tally-amber transition-all duration-300"
              style={{ width: `${Math.min(100, telemetry.progress_pct || 0)}%` }}
            />
          </div>
          <span className="text-studio-300 tabular-nums shrink-0 hidden sm:inline">
            {Math.round(telemetry.progress_pct || 0)}%
          </span>
        </div>

        {/* Live Hardware VRAM Gauge */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="flex items-center gap-2">
            <HardDrive className="w-3.5 h-3.5 text-studio-400" />
            <span className="text-studio-400 hidden md:inline">VRAM:</span>
            <span className="text-studio-200 tabular-nums">
              {vramUsed} <span className="text-studio-500">/ {vramTotal} MB</span>
            </span>
            <span
              className={`px-1.5 py-0.2 rounded text-[10px] tabular-nums font-medium ${
                vramPct > 85 ? "bg-tally-red/20 text-tally-red border border-tally-red/40" : "bg-studio-900 text-studio-300 border border-studio-800"
              }`}
            >
              {vramPct}%
            </span>
          </div>

          {/* Console Toggle */}
          <button
            onClick={() => setIsConsoleOpen(!isConsoleOpen)}
            className="p-1 rounded bg-studio-900 hover:bg-studio-850 border border-studio-800 text-studio-400 hover:text-white transition-colors"
            title="Toggle console log stream"
          >
            {isConsoleOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </div>
  );
};
