"use client";

import React, { useEffect, useState } from "react";
import {
  X,
  Settings as SettingsIcon,
  Cpu,
  Key,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Save,
} from "lucide-react";
import { GeminiTestResult, SettingsResponse, SystemStatus } from "@/types";
import { getSettings, getSystemStatus, testGemini, updateSettings } from "@/lib/api";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [settings, setSettings] = useState<SettingsResponse | null>(null);
  const [apiKey, setApiKey] = useState("");
  const [fastModel, setFastModel] = useState("gemini-4-hydrogen");
  const [deepModel, setDeepModel] = useState("gemini-4-neon");

  const [testResult, setTestResult] = useState<GeminiTestResult | null>(null);
  const [isTesting, setIsTesting] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (isOpen) {
      getSystemStatus().then(setStatus).catch(console.error);
      getSettings().then((res) => {
        setSettings(res);
        setFastModel(res.gemini_fast_model);
        setDeepModel(res.gemini_deep_model);
      }).catch(console.error);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleTestConnection = async () => {
    setIsTesting(true);
    setTestResult(null);
    try {
      const res = await testGemini();
      setTestResult(res);
    } catch (err: any) {
      setTestResult({
        success: false,
        error: err.message || "Connection test failed",
      });
    } finally {
      setIsTesting(false);
    }
  };

  const handleSaveSettings = async () => {
    setIsSaving(true);
    setSaveSuccess(false);
    try {
      await updateSettings({
        gemini_api_key: apiKey.trim() || undefined,
        gemini_fast_model: fastModel,
        gemini_deep_model: deepModel,
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2000);
    } catch (err) {
      console.error("Failed to save settings", err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#121218] border border-[#262636] rounded-xl max-w-xl w-full max-h-[90vh] flex flex-col p-5 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-[#262636]">
          <div>
            <h3 className="font-bold text-white text-sm tracking-tight flex items-center gap-2">
              <SettingsIcon className="w-4 h-4 text-[#00F0FF]" />
              <span>SETTINGS & HARDWARE DIAGNOSTICS</span>
            </h3>
            <p className="text-xs text-[#7E7E9A]">Configure Gemini API and inspect RTX 3050 capability</p>
          </div>
          <button
            onClick={onClose}
            className="text-[#7E7E9A] hover:text-white text-xs font-mono"
          >
            CLOSE [ESC]
          </button>
        </div>

        {/* Content */}
        <div className="py-4 space-y-5 overflow-y-auto flex-1">
          {/* Gemini API Key */}
          <div className="space-y-2">
            <label className="text-xs font-mono text-[#00F0FF] flex items-center gap-1.5">
              <Key className="w-3.5 h-3.5" />
              <span>GEMINI API KEY:</span>
            </label>
            <input
              type="password"
              placeholder={settings?.gemini_api_key_set ? "•••••••••••••••••••••••• (Configured)" : "Enter Gemini API Key..."}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="w-full bg-[#0A0A0F] border border-[#262636] focus:border-[#00F0FF] rounded-lg px-3 py-2 text-xs font-mono text-white placeholder-[#505068] outline-none"
            />
            <p className="text-[11px] text-[#7E7E9A]">
              Optional: Leave empty if using Zero-Cost Manual Gemini Web Mode.
            </p>
          </div>

          {/* Model Configuration */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-mono text-[#7E7E9A] block mb-1">
                FAST / SCORING MODEL:
              </label>
              <input
                type="text"
                value={fastModel}
                onChange={(e) => setFastModel(e.target.value)}
                className="w-full bg-[#0A0A0F] border border-[#262636] rounded-lg px-3 py-2 text-xs font-mono text-white outline-none"
              />
            </div>
            <div>
              <label className="text-xs font-mono text-[#7E7E9A] block mb-1">
                DEEP REASONING MODEL:
              </label>
              <input
                type="text"
                value={deepModel}
                onChange={(e) => setDeepModel(e.target.value)}
                className="w-full bg-[#0A0A0F] border border-[#262636] rounded-lg px-3 py-2 text-xs font-mono text-white outline-none"
              />
            </div>
          </div>

          {/* Test Connection Button & Result */}
          <div className="space-y-2">
            <button
              onClick={handleTestConnection}
              disabled={isTesting}
              className="px-4 py-2 bg-[#1A1A24] hover:bg-[#262636] border border-[#262636] text-[#00F0FF] rounded-lg text-xs font-mono flex items-center gap-2 transition-colors disabled:opacity-50"
            >
              {isTesting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
              <span>TEST GEMINI API & LIST MODELS</span>
            </button>

            {testResult && (
              <div
                className={`p-3 rounded-lg border text-xs font-mono space-y-1 ${
                  testResult.success
                    ? "bg-green-950/30 border-green-500/40 text-green-300"
                    : "bg-red-950/30 border-red-500/40 text-red-300"
                }`}
              >
                <div className="flex items-center gap-1.5 font-bold">
                  {testResult.success ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-green-400" />
                  ) : (
                    <AlertCircle className="w-3.5 h-3.5 text-red-400" />
                  )}
                  <span>{testResult.success ? "Gemini API Connected Successfully" : "Connection Failed"}</span>
                </div>
                {testResult.error && <p className="text-[11px] text-red-400">{testResult.error}</p>}
                {testResult.available_models && testResult.available_models.length > 0 && (
                  <p className="text-[11px] text-[#7E7E9A]">
                    Available Models: {testResult.available_models.slice(0, 4).join(", ")}...
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Hardware Diagnostics */}
          <div className="bg-[#0A0A0F] border border-[#262636] p-4 rounded-xl space-y-2 text-xs font-mono">
            <div className="text-[#00F0FF] font-bold flex items-center gap-1.5 mb-1">
              <Cpu className="w-3.5 h-3.5" />
              <span>HARDWARE DIAGNOSTIC REPORT:</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-[#7E7E9A]">
              <div>
                FFmpeg: <span className="text-white">{status?.ffmpeg_available ? "Available" : "Missing"}</span>
              </div>
              <div>
                NVENC GPU:{" "}
                <span className={status?.nvenc_available ? "text-[#00F0FF]" : "text-yellow-400"}>
                  {status?.nvenc_available ? "Available (RTX 3050)" : "Fallback (libx264)"}
                </span>
              </div>
              <div>
                CUDA PyTorch:{" "}
                <span className={status?.cuda_available ? "text-green-400" : "text-yellow-400"}>
                  {status?.cuda_available ? "Active" : "CPU Fallback"}
                </span>
              </div>
              <div>
                Total VRAM: <span className="text-white tabular-nums">{status?.vram_total_mb ?? 6144} MB</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-[#262636] flex items-center justify-between">
          <div className="text-xs text-green-400 font-mono">
            {saveSuccess && "Settings saved successfully!"}
          </div>
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-[#1A1A24] text-xs font-mono text-[#E2E2F0]"
            >
              Cancel
            </button>
            <button
              onClick={handleSaveSettings}
              disabled={isSaving}
              className="px-5 py-2 bg-gradient-to-r from-[#FF2E93] to-[#00F0FF] text-black font-bold font-mono text-xs rounded-lg hover:opacity-90 disabled:opacity-40 flex items-center gap-1.5 transition-all"
            >
              {isSaving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
              <span>SAVE SETTINGS</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
