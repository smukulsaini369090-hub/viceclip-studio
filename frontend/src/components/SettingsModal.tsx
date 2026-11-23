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
      <div className="bg-studio-900 border border-studio-700/80 rounded-lg max-w-xl w-full max-h-[90vh] flex flex-col p-5 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-studio-800">
          <div>
            <h3 className="font-medium text-studio-100 text-sm tracking-tight flex items-center gap-2">
              <SettingsIcon className="w-4 h-4 text-studio-400" />
              <span>Settings & hardware diagnostics</span>
            </h3>
            <p className="text-xs text-studio-400 mt-0.5">Configure Gemini API and inspect hardware acceleration</p>
          </div>
          <button
            onClick={onClose}
            className="text-studio-400 hover:text-white text-xs font-mono"
          >
            Close [Esc]
          </button>
        </div>

        {/* Content */}
        <div className="py-4 space-y-5 overflow-y-auto flex-1">
          {/* Gemini API Key */}
          <div className="space-y-2">
            <label className="text-xs font-mono text-studio-300 flex items-center gap-1.5 font-medium">
              <Key className="w-3.5 h-3.5 text-studio-400" />
              <span>Gemini API key:</span>
            </label>
            <input
              type="password"
              placeholder={settings?.gemini_api_key_set ? "•••••••••••••••••••••••• (Configured)" : "Enter Gemini API Key..."}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="w-full bg-studio-950 border border-studio-800 focus:border-studio-600 rounded px-3 py-2 text-xs font-mono text-studio-100 placeholder-studio-600 outline-none"
            />
            <p className="text-[11px] text-studio-500">
              Optional: Leave empty if using Zero-Cost Manual Gemini Web Mode.
            </p>
          </div>

          {/* Model Configuration */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-mono text-studio-400 block mb-1">
                Fast / scoring model:
              </label>
              <input
                type="text"
                value={fastModel}
                onChange={(e) => setFastModel(e.target.value)}
                className="w-full bg-studio-950 border border-studio-800 focus:border-studio-600 rounded px-3 py-2 text-xs font-mono text-studio-100 outline-none"
              />
            </div>
            <div>
              <label className="text-xs font-mono text-studio-400 block mb-1">
                Deep reasoning model:
              </label>
              <input
                type="text"
                value={deepModel}
                onChange={(e) => setDeepModel(e.target.value)}
                className="w-full bg-studio-950 border border-studio-800 focus:border-studio-600 rounded px-3 py-2 text-xs font-mono text-studio-100 outline-none"
              />
            </div>
          </div>

          {/* Test Connection Button & Result */}
          <div className="space-y-2">
            <button
              onClick={handleTestConnection}
              disabled={isTesting}
              className="px-4 py-2 bg-studio-800 hover:bg-studio-750 border border-studio-700 text-studio-200 hover:text-white rounded text-xs font-mono flex items-center gap-2 transition-colors disabled:opacity-50"
            >
              {isTesting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5 text-tally-amber" />}
              <span>Test Gemini API & list models</span>
            </button>

            {testResult && (
              <div
                className={`p-3 rounded border text-xs font-mono space-y-1 ${
                  testResult.success
                    ? "bg-studio-950 border-tally-emerald/40 text-tally-emerald"
                    : "bg-studio-950 border-tally-red/40 text-tally-red"
                }`}
              >
                <div className="flex items-center gap-1.5 font-medium">
                  {testResult.success ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-tally-emerald" />
                  ) : (
                    <AlertCircle className="w-3.5 h-3.5 text-tally-red" />
                  )}
                  <span>{testResult.success ? "Gemini API connected successfully" : "Connection failed"}</span>
                </div>
                {testResult.error && <p className="text-[11px] text-tally-red">{testResult.error}</p>}
                {testResult.available_models && testResult.available_models.length > 0 && (
                  <p className="text-[11px] text-studio-400">
                    Available models: {testResult.available_models.slice(0, 4).join(", ")}...
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Hardware Diagnostics */}
          <div className="bg-studio-950 border border-studio-800 p-4 rounded space-y-2 text-xs font-mono">
            <div className="text-studio-200 font-medium flex items-center gap-1.5 mb-1">
              <Cpu className="w-3.5 h-3.5 text-studio-400" />
              <span>Hardware diagnostics:</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-studio-400">
              <div>
                FFmpeg: <span className="text-studio-100">{status?.ffmpeg_available ? "Available" : "Missing"}</span>
              </div>
              <div>
                NVENC GPU:{" "}
                <span className={status?.nvenc_available ? "text-tally-amber font-medium" : "text-studio-400"}>
                  {status?.nvenc_available ? "Available (RTX 3050)" : "Fallback (libx264)"}
                </span>
              </div>
              <div>
                CUDA PyTorch:{" "}
                <span className={status?.cuda_available ? "text-tally-emerald font-medium" : "text-studio-400"}>
                  {status?.cuda_available ? "Active" : "CPU fallback"}
                </span>
              </div>
              <div>
                Total VRAM: <span className="text-studio-100 tabular-nums">{status?.vram_total_mb ?? 6144} MB</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-studio-800 flex items-center justify-between">
          <div className="text-xs text-tally-emerald font-mono">
            {saveSuccess && "Settings saved successfully."}
          </div>
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded bg-studio-800 hover:bg-studio-700 text-xs font-mono text-studio-300 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSaveSettings}
              disabled={isSaving}
              className="px-5 py-2 bg-tally-amber hover:bg-amber-400 text-studio-950 font-medium font-mono text-xs rounded disabled:opacity-40 flex items-center gap-1.5 transition-colors shadow-sm"
            >
              {isSaving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
              <span>Save settings</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
