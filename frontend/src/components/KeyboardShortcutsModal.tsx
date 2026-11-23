"use client";

import React, { useEffect } from "react";
import { X, Keyboard, Command } from "lucide-react";

interface KeyboardShortcutsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface ShortcutItem {
  keys: string[];
  description: string;
  category: "Playback" | "Trimming" | "Navigation";
}

const SHORTCUTS: ShortcutItem[] = [
  { keys: ["Space", "K"], description: "Toggle play / pause", category: "Playback" },
  { keys: ["J"], description: "Seek backward 2 seconds", category: "Playback" },
  { keys: ["L"], description: "Seek forward 2 seconds", category: "Playback" },
  { keys: ["I"], description: "Set trim in-point (start)", category: "Trimming" },
  { keys: ["O"], description: "Set trim out-point (end)", category: "Trimming" },
  { keys: ["←"], description: "Step backward 0.1s frame nudge", category: "Trimming" },
  { keys: ["→"], description: "Step forward 0.1s frame nudge", category: "Trimming" },
  { keys: ["?"], description: "Open keyboard shortcuts guide", category: "Navigation" },
  { keys: ["Esc"], description: "Close any modal or drawer", category: "Navigation" },
];

export const KeyboardShortcutsModal: React.FC<KeyboardShortcutsModalProps> = ({
  isOpen,
  onClose,
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (["INPUT", "TEXTAREA"].includes((e.target as HTMLElement)?.tagName)) return;
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const categories = ["Playback", "Trimming", "Navigation"] as const;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-studio-900 border border-studio-700/80 rounded-lg max-w-lg w-full max-h-[85vh] flex flex-col p-5 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-studio-800">
          <div>
            <h3 className="font-medium text-studio-100 text-sm tracking-tight flex items-center gap-2">
              <Keyboard className="w-4 h-4 text-tally-amber" />
              <span>Keyboard shortcuts</span>
            </h3>
            <p className="text-xs text-studio-400 mt-0.5">Hardware NLE editing hotkeys</p>
          </div>
          <button
            onClick={onClose}
            className="text-studio-400 hover:text-white text-xs font-mono p-1 rounded hover:bg-studio-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Shortcuts List */}
        <div className="py-4 space-y-5 overflow-y-auto flex-1">
          {categories.map((cat) => (
            <div key={cat} className="space-y-2">
              <div className="text-[11px] font-mono text-studio-400 uppercase tracking-wider font-medium">
                {cat}
              </div>
              <div className="space-y-1.5">
                {SHORTCUTS.filter((s) => s.category === cat).map((item, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between py-1.5 px-2.5 rounded bg-studio-950 border border-studio-800 text-xs font-mono"
                  >
                    <span className="text-studio-200">{item.description}</span>
                    <div className="flex items-center gap-1">
                      {item.keys.map((k, kIdx) => (
                        <kbd
                          key={kIdx}
                          className="px-2 py-0.5 rounded bg-studio-850 border border-studio-700 text-studio-100 text-[11px] shadow-sm font-semibold"
                        >
                          {k}
                        </kbd>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-studio-800 flex items-center justify-between text-[11px] font-mono text-studio-500">
          <span>Press <kbd className="px-1.5 py-0.5 rounded bg-studio-800 border border-studio-700 text-studio-300">?</kbd> anywhere to toggle this guide</span>
          <button
            onClick={onClose}
            className="px-3 py-1 bg-studio-800 hover:bg-studio-700 text-studio-200 rounded text-xs transition-colors"
          >
            Dismiss
          </button>
        </div>
      </div>
    </div>
  );
};
