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
      <div className="bg-studio-900 border border-studio-700/80 rounded-lg max-w-4xl w-full max-h-[90vh] flex flex-col p-5 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-studio-800">
          <div>
            <h3 className="font-medium text-studio-100 text-sm tracking-tight flex items-center gap-2">
              <Trophy className="w-4 h-4 text-tally-amber" />
              <span>Retention vault</span>
            </h3>
            <p className="text-xs text-studio-400 mt-0.5">
              Winning hook formulas injected into future script analysis prompts
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-studio-400 hover:text-white text-xs font-mono"
          >
            Close [Esc]
          </button>
        </div>

        {/* Content */}
        <div className="py-4 space-y-6 overflow-y-auto flex-1">
          {/* Top-5 Winners Showcase */}
          <div className="space-y-2">
            <div className="text-xs font-mono text-studio-300 flex items-center gap-1.5 font-medium">
              <Trophy className="w-3.5 h-3.5 text-tally-amber" />
              <span>Top winning hook formulas (prompt injection)</span>
            </div>
            {winners.length === 0 ? (
              <div className="p-3 bg-studio-950 border border-studio-800 rounded text-xs font-mono text-studio-500">
                No winners logged yet. Log your first 48-hour YouTube Shorts analytics below.
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {winners.map((w, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-studio-950 border border-studio-800 rounded flex flex-col gap-1 text-xs font-mono"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-studio-100 truncate">"{w.title_hook}"</span>
                      <span className="px-1.5 py-0.5 rounded bg-tally-amber/10 border border-tally-amber/30 text-tally-amber text-[10px] tabular-nums font-medium">
                        AVD: {w.avd_pct}%
                      </span>
                    </div>
                    <div className="text-[11px] text-studio-400 flex items-center gap-3">
                      <span>Views: <span className="text-studio-200 tabular-nums">{w.views_48h?.toLocaleString()}</span></span>
                      <span>Formula: <span className="text-studio-300">{w.hook_formula || "Curiosity"}</span></span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Log New Performance Form */}
          <form onSubmit={handleCreate} className="bg-studio-950 border border-studio-800 p-4 rounded-lg space-y-3">
            <div className="text-xs font-mono text-studio-300 flex items-center gap-1.5 font-medium">
              <BarChart3 className="w-3.5 h-3.5 text-studio-400" />
              <span>Log 48-hour Shorts analytics:</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="sm:col-span-3">
                <input
                  type="text"
                  placeholder="Short Title / Opening Hook line"
                  value={titleHook}
                  onChange={(e) => setTitleHook(e.target.value)}
                  className="w-full bg-studio-900 border border-studio-800 rounded px-3 py-2 text-xs text-studio-100 placeholder-studio-600 outline-none focus:border-studio-600"
                  required
                />
              </div>

              <div>
                <input
                  type="number"
                  placeholder="48h Views (e.g. 85000)"
                  value={views48h}
                  onChange={(e) => setViews48h(e.target.value)}
                  className="w-full bg-studio-900 border border-studio-800 rounded px-3 py-2 text-xs font-mono text-studio-100 placeholder-studio-600 outline-none focus:border-studio-600"
                />
              </div>

              <div>
                <input
                  type="number"
                  step="0.1"
                  placeholder="AVD % (e.g. 112.5)"
                  value={avdPct}
                  onChange={(e) => setAvdPct(e.target.value)}
                  className="w-full bg-studio-900 border border-studio-800 rounded px-3 py-2 text-xs font-mono text-studio-100 placeholder-studio-600 outline-none focus:border-studio-600"
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
                  className="w-full bg-studio-900 border border-studio-800 rounded px-3 py-2 text-xs font-mono text-studio-100 placeholder-studio-600 outline-none focus:border-studio-600"
                />
              </div>

              <div>
                <input
                  type="text"
                  placeholder="Hook Archetype (e.g., Hidden Detail)"
                  value={hookFormula}
                  onChange={(e) => setHookFormula(e.target.value)}
                  className="w-full bg-studio-900 border border-studio-800 rounded px-3 py-2 text-xs font-mono text-studio-100 placeholder-studio-600 outline-none focus:border-studio-600"
                />
              </div>

              <div className="sm:col-span-2">
                <input
                  type="text"
                  placeholder="Clip Pattern (e.g., Infinite Loop + Sound Spike)"
                  value={clipPattern}
                  onChange={(e) => setClipPattern(e.target.value)}
                  className="w-full bg-studio-900 border border-studio-800 rounded px-3 py-2 text-xs font-mono text-studio-100 placeholder-studio-600 outline-none focus:border-studio-600"
                />
              </div>
            </div>

            <div className="flex justify-end pt-1">
              <button
                type="submit"
                className="px-4 py-2 bg-tally-amber hover:bg-amber-400 text-studio-950 font-medium font-mono text-xs rounded flex items-center gap-1.5 transition-colors shadow-sm"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Log to vault</span>
              </button>
            </div>
          </form>

          {/* Historical Analytics Table */}
          <div className="space-y-2">
            <div className="text-xs font-mono text-studio-400">Logged clips ({entries.length}):</div>
            <div className="border border-studio-800 rounded overflow-hidden">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-studio-950 text-studio-400 border-b border-studio-800">
                  <tr>
                    <th className="p-2.5">Title / Hook</th>
                    <th className="p-2.5">Views</th>
                    <th className="p-2.5">AVD %</th>
                    <th className="p-2.5">Viewed %</th>
                    <th className="p-2.5">Hook Pattern</th>
                    <th className="p-2.5 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-studio-850">
                  {entries.map((entry) => (
                    <tr key={entry.id} className="hover:bg-studio-850/50 transition-colors">
                      <td className="p-2.5 text-studio-200 max-w-[200px] truncate">{entry.title_hook}</td>
                      <td className="p-2.5 text-studio-200 tabular-nums">{entry.views_48h?.toLocaleString()}</td>
                      <td className="p-2.5 text-tally-amber tabular-nums font-medium">{entry.avd_pct}%</td>
                      <td className="p-2.5 text-studio-300 tabular-nums">{entry.viewed_pct}%</td>
                      <td className="p-2.5 text-studio-400">{entry.hook_formula || "—"}</td>
                      <td className="p-2.5 text-right">
                        <button
                          onClick={() => entry.id && handleDelete(entry.id)}
                          className="p-1 text-studio-500 hover:text-tally-red transition-colors"
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
