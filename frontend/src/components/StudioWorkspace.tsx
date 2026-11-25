"use client";

import React, { useState } from "react";
import {
  Play,
  Copy,
  Check,
  Code,
  Shield,
  Mic,
  ZoomIn,
  Scissors,
  Split,
  Sparkles,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { RenderSettings } from "@/types";
import { parseManualGemini } from "@/lib/api";

interface StudioWorkspaceProps {
  url: string;
  setUrl: (url: string) => void;
  settings: RenderSettings;
  setSettings: React.Dispatch<React.SetStateAction<RenderSettings>>;
  onAnalyze: () => void;
  isAnalyzing: boolean;
  manualPrompt: string | null;
  videoId: string | null;
  onManualClipsLoaded: (clips: any[]) => void;
}

export const StudioWorkspace: React.FC<StudioWorkspaceProps> = ({
  url,
  setUrl,
  settings,
  setSettings,
  onAnalyze,
  isAnalyzing,
  manualPrompt,
  videoId,
  onManualClipsLoaded,
}) => {
  const [showManualModal, setShowManualModal] = useState(false);
  const [copied, setCopied] = useState(false);
  const [pastedJson, setPastedJson] = useState("");
  const [parseError, setParseError] = useState<string | null>(null);
  const [isParsing, setIsParsing] = useState(false);

  const handleCopyPrompt = async () => {
    if (!manualPrompt) return;
    try {
      await navigator.clipboard.writeText(manualPrompt);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy prompt", err);
    }
  };

  const handleIngestJson = async () => {
    if (!videoId || !pastedJson.trim()) return;
    setIsParsing(true);
    setParseError(null);
    try {
      const res = await parseManualGemini(videoId, pastedJson);
      onManualClipsLoaded(res.clips);
      setShowManualModal(false);
      setPastedJson("");
    } catch (err: any) {
      setParseError(err.message || "Failed to parse JSON");
    } finally {
      setIsParsing(false);
    }
  };

  const toggleSetting = (key: keyof RenderSettings) => {
    setSettings((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  return (
    <div className="bg-studio-800 border border-studio-600 rounded-xl p-4 sm:p-5 shadow-studio-card">
      {/* URL Input Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste YouTube URL or video ID (e.g. https://youtu.be/...)"
            disabled={isAnalyzing}
            className="w-full bg-studio-950 border border-studio-600 focus:border-studio-400 rounded-lg px-3.5 py-2.5 text-xs font-mono text-studio-100 placeholder-studio-400 outline-none transition-colors disabled:opacity-50"
          />
        </div>
        <button
          onClick={onAnalyze}
          disabled={isAnalyzing || !url.trim()}
          className="px-5 py-2.5 bg-studio-100 hover:bg-white disabled:opacity-40 text-studio-950 font-medium text-xs rounded-lg transition-colors flex items-center justify-center gap-2 shadow-studio-raised disabled:shadow-none whitespace-nowrap"
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>Analyzing…</span>
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Analyze video</span>
            </>
          )}
        </button>
      </div>

      {/* Feature Toggles Strip */}
      <div className="mt-3.5 pt-3.5 border-t border-studio-600 flex flex-wrap items-center gap-1.5">
        <span className="text-[11px] font-mono text-studio-400 mr-1.5">
          Pipeline modes:
        </span>

        {/* Demucs */}
        <button
          onClick={() => toggleSetting("enable_demucs")}
          className={`px-2.5 py-1 rounded-md text-[11px] font-mono border transition-all flex items-center gap-1.5 ${
            settings.enable_demucs
              ? "bg-studio-700 border-studio-400 text-studio-100"
              : "bg-studio-950 border-studio-600 text-studio-400 hover:border-studio-500 hover:text-studio-300"
          }`}
          title="Demucs stem separation: removes copyrighted radio music while keeping speech + SFX"
        >
          <span className={`w-1.5 h-1.5 rounded-full ${settings.enable_demucs ? "bg-tally-amber" : "bg-transparent"}`} />
          <Shield className="w-3 h-3 text-studio-400" />
          <span>Copyright Shield</span>
        </button>

        {/* Commentary */}
        <button
          onClick={() => toggleSetting("enable_commentary")}
          className={`px-2.5 py-1 rounded-md text-[11px] font-mono border transition-all flex items-center gap-1.5 ${
            settings.enable_commentary
              ? "bg-studio-700 border-studio-400 text-studio-100"
              : "bg-studio-950 border-studio-600 text-studio-400 hover:border-studio-500 hover:text-studio-300"
          }`}
          title="Transformative AI voiceover via edge-tts (Anti-Reused Content)"
        >
          <span className={`w-1.5 h-1.5 rounded-full ${settings.enable_commentary ? "bg-tally-amber" : "bg-transparent"}`} />
          <Mic className="w-3 h-3 text-studio-400" />
          <span>Transformative Commentary</span>
        </button>

        {/* Easter Egg Zoom */}
        <button
          onClick={() => toggleSetting("enable_easter_egg_zoom")}
          className={`px-2.5 py-1 rounded-md text-[11px] font-mono border transition-all flex items-center gap-1.5 ${
            settings.enable_easter_egg_zoom
              ? "bg-studio-700 border-studio-400 text-studio-100"
              : "bg-studio-950 border-studio-600 text-studio-400 hover:border-studio-500 hover:text-studio-300"
          }`}
          title="God-Mode Easter-Egg Auto-Zoom: Gemini Vision detects coordinates for smooth zoom callout"
        >
          <span className={`w-1.5 h-1.5 rounded-full ${settings.enable_easter_egg_zoom ? "bg-tally-amber" : "bg-transparent"}`} />
          <ZoomIn className="w-3 h-3 text-studio-400" />
          <span>Easter-Egg Zoom</span>
        </button>

        {/* Dead Air Cut */}
        <button
          onClick={() => toggleSetting("enable_dead_air_cut")}
          className={`px-2.5 py-1 rounded-md text-[11px] font-mono border transition-all flex items-center gap-1.5 ${
            settings.enable_dead_air_cut
              ? "bg-studio-700 border-studio-400 text-studio-100"
              : "bg-studio-950 border-studio-600 text-studio-400 hover:border-studio-500 hover:text-studio-300"
          }`}
          title="Splices out silence > 0.4s with smooth audio crossfades"
        >
          <span className={`w-1.5 h-1.5 rounded-full ${settings.enable_dead_air_cut ? "bg-tally-amber" : "bg-transparent"}`} />
          <Scissors className="w-3 h-3 text-studio-400" />
          <span>Dead-Air Cut</span>
        </button>

        {/* Dual Hook */}
        <button
          onClick={() => toggleSetting("enable_dual_hook")}
          className={`px-2.5 py-1 rounded-md text-[11px] font-mono border transition-all flex items-center gap-1.5 ${
            settings.enable_dual_hook
              ? "bg-studio-700 border-studio-400 text-studio-100"
              : "bg-studio-950 border-studio-600 text-studio-400 hover:border-studio-500 hover:text-studio-300"
          }`}
          title="Renders Variant A & Variant B with different curiosity banners for A/B testing"
        >
          <span className={`w-1.5 h-1.5 rounded-full ${settings.enable_dual_hook ? "bg-tally-amber" : "bg-transparent"}`} />
          <Split className="w-3 h-3 text-studio-400" />
          <span>Dual-Hook A/B</span>
        </button>

        {/* Manual Web Mode Toggle */}
        <button
          onClick={() => toggleSetting("manual_gemini_mode")}
          className={`px-2.5 py-1 rounded-md text-[11px] font-mono border transition-all flex items-center gap-1.5 ${
            settings.manual_gemini_mode
              ? "bg-studio-700 border-studio-400 text-studio-100"
              : "bg-studio-950 border-studio-600 text-studio-400 hover:border-studio-500 hover:text-studio-300"
          }`}
          title="Zero-cost mode: Copy compiled prompt to gemini.google.com and paste response back"
        >
          <Code className="w-3.5 h-3.5" />
          <span>Manual Gemini Web Mode</span>
        </button>

        {/* Open Manual Modal Button if prompt is ready */}
        {manualPrompt && (
          <button
            onClick={() => setShowManualModal(true)}
            className="ml-auto px-3 py-1.5 rounded-md bg-studio-700 hover:bg-studio-650 border border-tally-amber/40 text-tally-amber hover:text-white text-xs font-mono tracking-tight transition-all flex items-center gap-1.5 btn-tactile shadow-studio-card"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Open manual prompt ingest</span>
          </button>
        )}
      </div>

      {/* Manual Gemini Web Mode Modal */}
      {showManualModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-studio-900 border border-studio-700/80 rounded-xl max-w-2xl w-full max-h-[90vh] flex flex-col p-5 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-studio-800">
              <div>
                <h3 className="font-medium text-studio-100 text-sm tracking-tight flex items-center gap-2">
                  <Code className="w-4 h-4 text-studio-400" />
                  <span>Manual Gemini web ingest</span>
                </h3>
                <p className="text-xs text-studio-400 mt-0.5">Zero-cost unlimited fallback mode</p>
              </div>
              <button
                onClick={() => setShowManualModal(false)}
                className="text-studio-400 hover:text-white text-xs font-mono"
              >
                Close [Esc]
              </button>
            </div>

            <div className="py-4 space-y-4 overflow-y-auto flex-1">
              {/* Step 1: Copy Prompt */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono text-studio-300 font-medium">
                    Step 1: Copy compiled prompt
                  </span>
                  <button
                    onClick={handleCopyPrompt}
                    className="px-3 py-1 bg-studio-800 hover:bg-studio-750 border border-studio-700 text-studio-200 rounded text-xs font-mono flex items-center gap-1.5 btn-tactile transition-colors"
                  >
                    {copied ? <Check className="w-3 h-3 text-tally-emerald" /> : <Copy className="w-3 h-3 text-studio-400" />}
                    <span>{copied ? "Copied" : "Copy prompt"}</span>
                  </button>
                </div>
                <div className="max-h-28 overflow-y-auto p-2.5 bg-studio-950 border border-studio-800 rounded text-[11px] font-mono text-studio-400 whitespace-pre-wrap select-all">
                  {manualPrompt}
                </div>
              </div>

              {/* Step 2: Paste JSON */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono text-studio-300 font-medium">
                    Step 2: Paste JSON from gemini.google.com
                  </span>
                </div>
                <textarea
                  value={pastedJson}
                  onChange={(e) => setPastedJson(e.target.value)}
                  placeholder="Paste the raw response from Gemini here (markdown code fences ```json are automatically stripped)..."
                  rows={8}
                  className="w-full bg-studio-950 border border-studio-700 focus:border-tally-amber rounded-lg p-3 text-xs font-mono text-studio-100 placeholder-studio-500 outline-none transition-colors"
                />
              </div>

              {parseError && (
                <div className="p-3 rounded-lg bg-red-950/40 border border-red-500/50 flex items-start gap-2 text-xs text-red-300">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-400" />
                  <span>{parseError}</span>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-studio-800 flex justify-end gap-2">
              <button
                onClick={() => setShowManualModal(false)}
                className="px-4 py-2 rounded-lg bg-studio-800 hover:bg-studio-750 border border-studio-700 text-xs font-mono text-studio-300 hover:text-white btn-tactile transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleIngestJson}
                disabled={isParsing || !pastedJson.trim()}
                className="px-5 py-2 bg-studio-100 hover:bg-white text-studio-950 font-medium text-xs font-mono rounded-lg hover:opacity-90 disabled:opacity-40 transition-all flex items-center gap-1.5 btn-tactile shadow-studio-raised"
              >
                {isParsing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
                <span>Validate & ingest clips</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
