"use client";

import React, { useEffect, useState } from "react";
import { X, Sparkles, Plus, Trash2, Trophy, BarChart3, Loader2 } from "lucide-react";
import { RetentionVaultEntry } from "@/types";
import { deleteVaultEntry, getVaultWinners, listVaultEntries, logVaultEntry } from "@/lib/api";

interface RetentionVaultModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const RetentionVaultModal: React.FC<RetentionVaultModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [entries, setEntries] = useState<RetentionVaultEntry[]>([]);
  const [winners, setWinners] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // New Log Form
  const [titleHook, setTitleHook] = useState("");
  const [views48h, setViews48h] = useState("");
  const [avdPct, setAvdPct] = useState("");
  const [viewedPct, setViewedPct] = useState("");
  const [hookFormula, setHookFormula] = useState("");
  const [clipPattern, setClipPattern] = useState("");

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [resAll, resWinners] = await Promise.all([
        listVaultEntries(),
        getVaultWinners(),
      ]);
      setEntries(resAll.entries);
      setWinners(resWinners.winners);
    } catch (err) {
      console.error("Failed to load vault data", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchData();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!titleHook.trim()) return;

    try {
      await logVaultEntry({
        clip_id: `manual_${Date.now()}`,
        video_id: "manual",
        title_hook: titleHook,
        views_48h: parseInt(views48h) || 0,
        avd_pct: parseFloat(avdPct) || 0,
        viewed_pct: parseFloat(viewedPct) || 0,
        swiped_pct: Math.max(0, 100 - (parseFloat(viewedPct) || 0)),
        hook_formula: hookFormula,
        clip_pattern: clipPattern,
        banner_text: "",
      });

      setTitleHook("");
      setViews48h("");
      setAvdPct("");
      setViewedPct("");
      setHookFormula("");
      setClipPattern("");

      await fetchData();
    } catch (err) {
      console.error("Failed to log vault entry", err);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteVaultEntry(id);
      await fetchData();
    } catch (err) {
      console.error("Failed to delete entry", err);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#121218] border border-[#262636] rounded-xl max-w-4xl w-full max-h-[90vh] flex flex-col p-5 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-[#262636]">
          <div>
            <h3 className="font-bold text-white text-sm tracking-tight flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#FFE600]" />
              <span>SELF-LEARNING RETENTION VAULT</span>
            </h3>
            <p className="text-xs text-[#7E7E9A]">
              Winning hook formulas injected directly into future Viral Brain prompts
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-[#7E7E9A] hover:text-white text-xs font-mono"
          >
            CLOSE [ESC]
          </button>
        </div>

        {/* Content */}
        <div className="py-4 space-y-6 overflow-y-auto flex-1">
          {/* Top-5 Winners Showcase */}
          <div className="space-y-2">
            <div className="text-xs font-mono text-[#FFE600] flex items-center gap-1.5">
              <Trophy className="w-3.5 h-3.5" />
              <span>TOP-5 WINNING HOOK FORMULAS (ACTIVE PROMPT INJECTION):</span>
            </div>
            {winners.length === 0 ? (
              <div className="p-3 bg-[#0A0A0F] border border-[#262636] rounded-lg text-xs font-mono text-[#505068]">
                No winners logged yet. Log your first 48-hour YouTube Shorts analytics below.
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {winners.map((w, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-[#0A0A0F] border border-[#FFE600]/30 rounded-lg flex flex-col gap-1 text-xs font-mono"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white truncate">"{w.title_hook}"</span>
                      <span className="px-1.5 py-0.5 rounded bg-[#FFE600]/15 text-[#FFE600] text-[10px] tabular-nums font-bold">
                        AVD: {w.avd_pct}%
                      </span>
                    </div>
                    <div className="text-[11px] text-[#7E7E9A] flex items-center gap-3">
                      <span>Views: <span className="text-white tabular-nums">{w.views_48h?.toLocaleString()}</span></span>
                      <span>Formula: <span className="text-[#00F0FF]">{w.hook_formula || "Curiosity"}</span></span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Log New Performance Form */}
          <form onSubmit={handleCreate} className="bg-[#0A0A0F] border border-[#262636] p-4 rounded-xl space-y-3">
            <div className="text-xs font-mono text-[#00F0FF] flex items-center gap-1.5">
              <BarChart3 className="w-3.5 h-3.5" />
              <span>LOG 48-HOUR SHORTS ANALYTICS:</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="sm:col-span-3">
                <input
                  type="text"
                  placeholder="Short Title / Opening Hook line"
                  value={titleHook}
                  onChange={(e) => setTitleHook(e.target.value)}
                  className="w-full bg-[#121218] border border-[#262636] rounded-lg px-3 py-2 text-xs text-white placeholder-[#505068] outline-none"
                  required
                />
              </div>

              <div>
                <input
                  type="number"
                  placeholder="48h Views (e.g. 85000)"
                  value={views48h}
                  onChange={(e) => setViews48h(e.target.value)}
                  className="w-full bg-[#121218] border border-[#262636] rounded-lg px-3 py-2 text-xs font-mono text-white placeholder-[#505068] outline-none"
                />
              </div>

              <div>
                <input
                  type="number"
                  step="0.1"
                  placeholder="AVD % (e.g. 112.5)"
                  value={avdPct}
                  onChange={(e) => setAvdPct(e.target.value)}
                  className="w-full bg-[#121218] border border-[#262636] rounded-lg px-3 py-2 text-xs font-mono text-white placeholder-[#505068] outline-none"
                  required
                />
              </div>

              <div>
                <input
                  type="number"
                  step="0.1"
                  placeholder="Viewed vs Swiped % (e.g. 78.4)"
                  value={viewedPct}
                  onChange={(e) => setViewedPct(e.target.value)}
                  className="w-full bg-[#121218] border border-[#262636] rounded-lg px-3 py-2 text-xs font-mono text-white placeholder-[#505068] outline-none"
                />
              </div>

              <div>
                <input
                  type="text"
                  placeholder="Hook Archetype (e.g., Hidden Detail)"
                  value={hookFormula}
                  onChange={(e) => setHookFormula(e.target.value)}
                  className="w-full bg-[#121218] border border-[#262636] rounded-lg px-3 py-2 text-xs font-mono text-white placeholder-[#505068] outline-none"
                />
              </div>

              <div className="sm:col-span-2">
                <input
                  type="text"
                  placeholder="Clip Pattern (e.g., Infinite Loop + Sound Spike)"
                  value={clipPattern}
                  onChange={(e) => setClipPattern(e.target.value)}
                  className="w-full bg-[#121218] border border-[#262636] rounded-lg px-3 py-2 text-xs font-mono text-white placeholder-[#505068] outline-none"
                />
              </div>
            </div>

            <div className="flex justify-end pt-1">
              <button
                type="submit"
                className="px-4 py-2 bg-gradient-to-r from-[#FF2E93] to-[#00F0FF] text-black font-bold font-mono text-xs rounded-lg hover:opacity-90 flex items-center gap-1.5 transition-all shadow-neon-pink"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>LOG TO RETENTION VAULT</span>
              </button>
            </div>
          </form>

          {/* Historical Analytics Table */}
          <div className="space-y-2">
            <div className="text-xs font-mono text-[#7E7E9A]">LOGGED CLIPS ({entries.length}):</div>
            <div className="border border-[#262636] rounded-lg overflow-hidden">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-[#0A0A0F] text-[#7E7E9A] border-b border-[#262636]">
                  <tr>
                    <th className="p-2.5">Title / Hook</th>
                    <th className="p-2.5">Views</th>
                    <th className="p-2.5">AVD %</th>
                    <th className="p-2.5">Viewed %</th>
                    <th className="p-2.5">Hook Pattern</th>
                    <th className="p-2.5 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1A1A24]">
                  {entries.map((entry) => (
                    <tr key={entry.id} className="hover:bg-[#1A1A24]/40">
                      <td className="p-2.5 text-white max-w-[200px] truncate">{entry.title_hook}</td>
                      <td className="p-2.5 text-[#00F0FF] tabular-nums">{entry.views_48h?.toLocaleString()}</td>
                      <td className="p-2.5 text-[#FFE600] tabular-nums font-bold">{entry.avd_pct}%</td>
                      <td className="p-2.5 text-white tabular-nums">{entry.viewed_pct}%</td>
                      <td className="p-2.5 text-[#7E7E9A]">{entry.hook_formula || "—"}</td>
                      <td className="p-2.5 text-right">
                        <button
                          onClick={() => entry.id && handleDelete(entry.id)}
                          className="p-1 text-[#7E7E9A] hover:text-red-400"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
