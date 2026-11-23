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
    <div className="bg-[#121218] border border-[#262636] rounded-xl p-4 sm:p-5 shadow-studio-glow">
      {/* URL Input Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste YouTube URL or Video ID (e.g., https://youtu.be/...)"
            disabled={isAnalyzing}
            className="w-full bg-[#0A0A0F] border border-[#262636] focus:border-[#00F0FF] rounded-lg px-4 py-3 text-sm text-white placeholder-[#505068] outline-none transition-all disabled:opacity-50"
          />
        </div>
        <button
          onClick={onAnalyze}
          disabled={isAnalyzing || !url.trim()}
          className="px-6 py-3 bg-gradient-to-r from-[#FF2E93] to-[#00F0FF] hover:opacity-90 disabled:opacity-40 text-black font-bold text-sm tracking-wider rounded-lg transition-all flex items-center justify-center gap-2 shadow-neon-pink disabled:shadow-none whitespace-nowrap"
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>ANALYZING...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>ANALYZE VIDEO</span>
            </>
          )}
        </button>
      </div>

      {/* Feature Toggles Strip */}
      <div className="mt-4 pt-4 border-t border-[#1E1E2A] flex flex-wrap items-center gap-2">
        <span className="text-[11px] font-mono tracking-wider text-[#7E7E9A] mr-1">
          PIPELINE MODES:
        </span>

        {/* Demucs */}
        <button
          onClick={() => toggleSetting("enable_demucs")}
          className={`px-2.5 py-1.5 rounded-md text-xs font-mono border transition-all flex items-center gap-1.5 ${
            settings.enable_demucs
              ? "bg-[#FF2E93]/15 border-[#FF2E93] text-[#FF2E93]"
              : "bg-[#0A0A0F] border-[#262636] text-[#7E7E9A] hover:border-[#505068]"
          }`}
          title="Demucs stem separation: removes copyrighted radio music while keeping speech + SFX"
        >
          <Shield className="w-3.5 h-3.5" />
          <span>Copyright Shield</span>
        </button>

        {/* Commentary */}
        <button
          onClick={() => toggleSetting("enable_commentary")}
          className={`px-2.5 py-1.5 rounded-md text-xs font-mono border transition-all flex items-center gap-1.5 ${
            settings.enable_commentary
              ? "bg-[#00F0FF]/15 border-[#00F0FF] text-[#00F0FF]"
              : "bg-[#0A0A0F] border-[#262636] text-[#7E7E9A] hover:border-[#505068]"
          }`}
          title="Transformative AI voiceover via edge-tts (Anti-Reused Content)"
        >
          <Mic className="w-3.5 h-3.5" />
          <span>Transformative Commentary</span>
        </button>

        {/* Easter Egg Zoom */}
        <button
          onClick={() => toggleSetting("enable_easter_egg_zoom")}
          className={`px-2.5 py-1.5 rounded-md text-xs font-mono border transition-all flex items-center gap-1.5 ${
            settings.enable_easter_egg_zoom
              ? "bg-[#FFE600]/15 border-[#FFE600] text-[#FFE600]"
              : "bg-[#0A0A0F] border-[#262636] text-[#7E7E9A] hover:border-[#505068]"
          }`}
          title="God-Mode Easter-Egg Auto-Zoom: Gemini Vision detects coordinates for smooth zoom callout"
        >
          <ZoomIn className="w-3.5 h-3.5" />
          <span>Easter-Egg Zoom</span>
        </button>

        {/* Dead Air Cut */}
        <button
          onClick={() => toggleSetting("enable_dead_air_cut")}
          className={`px-2.5 py-1.5 rounded-md text-xs font-mono border transition-all flex items-center gap-1.5 ${
            settings.enable_dead_air_cut
              ? "bg-[#00F0FF]/15 border-[#00F0FF] text-[#00F0FF]"
              : "bg-[#0A0A0F] border-[#262636] text-[#7E7E9A] hover:border-[#505068]"
          }`}
          title="Splices out silence > 0.4s with smooth audio crossfades"
        >
          <Scissors className="w-3.5 h-3.5" />
          <span>Dead-Air Cut</span>
        </button>

        {/* Dual Hook */}
        <button
          onClick={() => toggleSetting("enable_dual_hook")}
          className={`px-2.5 py-1.5 rounded-md text-xs font-mono border transition-all flex items-center gap-1.5 ${
            settings.enable_dual_hook
              ? "bg-[#FF2E93]/15 border-[#FF2E93] text-[#FF2E93]"
              : "bg-[#0A0A0F] border-[#262636] text-[#7E7E9A] hover:border-[#505068]"
          }`}
          title="Renders Variant A & Variant B with different curiosity banners for A/B testing"
        >
          <Split className="w-3.5 h-3.5" />
          <span>Dual-Hook A/B</span>
        </button>

        {/* Manual Web Mode Toggle */}
        <button
          onClick={() => toggleSetting("manual_gemini_mode")}
          className={`px-2.5 py-1.5 rounded-md text-xs font-mono border transition-all flex items-center gap-1.5 ${
            settings.manual_gemini_mode
              ? "bg-[#9D00FF]/20 border-[#9D00FF] text-white"
              : "bg-[#0A0A0F] border-[#262636] text-[#7E7E9A] hover:border-[#505068]"
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
            className="ml-auto px-3 py-1.5 rounded-md bg-[#9D00FF] hover:bg-[#8A00E0] text-white text-xs font-mono tracking-wider transition-all flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Open Manual Ingest Modal</span>
          </button>
        )}
      </div>

      {/* Manual Gemini Web Mode Modal */}
      {showManualModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#121218] border border-[#262636] rounded-xl max-w-2xl w-full max-h-[90vh] flex flex-col p-5 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-[#262636]">
              <div>
                <h3 className="font-bold text-white text-sm">MANUAL GEMINI WEB INGEST</h3>
                <p className="text-xs text-[#7E7E9A]">Zero-cost unlimited fallback mode</p>
              </div>
              <button
                onClick={() => setShowManualModal(false)}
                className="text-[#7E7E9A] hover:text-white text-xs font-mono"
              >
                CLOSE [ESC]
              </button>
            </div>

            <div className="py-4 space-y-4 overflow-y-auto flex-1">
              {/* Step 1: Copy Prompt */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono text-[#00F0FF]">
                    STEP 1: Copy compiled prompt
                  </span>
                  <button
                    onClick={handleCopyPrompt}
                    className="px-3 py-1 bg-[#1A1A24] hover:bg-[#262636] border border-[#00F0FF]/30 text-[#00F0FF] rounded text-xs font-mono flex items-center gap-1.5"
                  >
                    {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                    <span>{copied ? "COPIED TO CLIPBOARD" : "COPY PROMPT"}</span>
                  </button>
                </div>
                <div className="max-h-28 overflow-y-auto p-2.5 bg-[#0A0A0F] border border-[#262636] rounded text-[11px] font-mono text-[#7E7E9A] whitespace-pre-wrap">
                  {manualPrompt}
                </div>
              </div>

              {/* Step 2: Paste JSON */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono text-[#FF2E93]">
                    STEP 2: Paste JSON from gemini.google.com
                  </span>
                </div>
                <textarea
                  value={pastedJson}
                  onChange={(e) => setPastedJson(e.target.value)}
                  placeholder="Paste the raw response from Gemini here (markdown code fences ```json are automatically stripped)..."
                  rows={8}
                  className="w-full bg-[#0A0A0F] border border-[#262636] focus:border-[#FF2E93] rounded-lg p-3 text-xs font-mono text-white placeholder-[#505068] outline-none"
                />
              </div>

              {parseError && (
                <div className="p-3 rounded-lg bg-red-950/40 border border-red-500/50 flex items-start gap-2 text-xs text-red-300">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-400" />
                  <span>{parseError}</span>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-[#262636] flex justify-end gap-2">
              <button
                onClick={() => setShowManualModal(false)}
                className="px-4 py-2 rounded-lg bg-[#1A1A24] text-xs font-mono text-[#E2E2F0]"
              >
                Cancel
              </button>
              <button
                onClick={handleIngestJson}
                disabled={isParsing || !pastedJson.trim()}
                className="px-5 py-2 bg-gradient-to-r from-[#FF2E93] to-[#00F0FF] text-black font-bold text-xs font-mono rounded-lg hover:opacity-90 disabled:opacity-40 transition-all flex items-center gap-1.5"
              >
                {isParsing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
                <span>VALIDATE & INGEST CLIPS</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
