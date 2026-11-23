"use client";

import React, { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { StudioWorkspace } from "@/components/StudioWorkspace";
import { HeatmapTimeline } from "@/components/HeatmapTimeline";
import { LayoutCaptionPlayground } from "@/components/LayoutCaptionPlayground";
import { ClipCandidateCard } from "@/components/ClipCandidateCard";
import { UploadKitDrawer } from "@/components/UploadKitDrawer";
import { BatchQueueModal } from "@/components/BatchQueueModal";
import { RetentionVaultModal } from "@/components/RetentionVaultModal";
import { SettingsModal } from "@/components/SettingsModal";
import { SmartCacheSidebar } from "@/components/SmartCacheSidebar";
import { TelemetryBar } from "@/components/TelemetryBar";
import { KeyboardShortcutsModal } from "@/components/KeyboardShortcutsModal";

import {
  AudioSpike,
  ClipCandidate,
  CropOverride,
  HeatmapPoint,
  RenderSettings,
  SystemStatus,
  VisualSpike,
} from "@/types";
import {
  analyzeVideo,
  getCachedVideo,
  getSystemStatus,
  renderClip,
} from "@/lib/api";
import { useTelemetry } from "@/lib/sse";
import { Film, Sparkles, Layers, AlertTriangle, CheckCircle2, X } from "lucide-react";

export default function StudioPage() {
  const { telemetry } = useTelemetry();

  // Hardware Status
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);

  // In-app Notifications
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Studio State
  const [url, setUrl] = useState("");
  const [settings, setSettings] = useState<RenderSettings>({
    enable_demucs: false,
    enable_commentary: false,
    enable_easter_egg_zoom: true,
    enable_dead_air_cut: true,
    enable_dual_hook: true,
    caption_theme: "vice_city_neon",
    manual_gemini_mode: false,
    commentary_voice: "en-US-GuyNeural",
  });

  // Active Video State
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeVideoId, setActiveVideoId] = useState<string | null>(null);
  const [videoTitle, setVideoTitle] = useState("");
  const [durationSec, setDurationSec] = useState(0);
  const [videoSrc, setVideoSrc] = useState("");
  const [heatmap, setHeatmap] = useState<HeatmapPoint[]>([]);
  const [audioSpikes, setAudioSpikes] = useState<AudioSpike[]>([]);
  const [visualSpikes, setVisualSpikes] = useState<VisualSpike[]>([]);

  // Candidate Clips State
  const [clips, setClips] = useState<ClipCandidate[]>([]);
  const [activeClip, setActiveClip] = useState<ClipCandidate | null>(null);
  const [renderingClipId, setRenderingClipId] = useState<string | null>(null);
  const [manualPrompt, setManualPrompt] = useState<string | null>(null);

  // Modals & Drawers
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isBatchOpen, setIsBatchOpen] = useState(false);
  const [isVaultOpen, setIsVaultOpen] = useState(false);
  const [isCacheOpen, setIsCacheOpen] = useState(false);
  const [isShortcutsOpen, setIsShortcutsOpen] = useState(false);
  const [uploadKitClip, setUploadKitClip] = useState<ClipCandidate | null>(null);

  // Global '?' shortcut key listener
  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if (["INPUT", "TEXTAREA"].includes((e.target as HTMLElement)?.tagName)) return;
      if (e.key === "?" || (e.shiftKey && e.key === "/")) {
        e.preventDefault();
        setIsShortcutsOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleGlobalKeyDown);
    return () => window.removeEventListener("keydown", handleGlobalKeyDown);
  }, []);

  // Initial Hardware Capability Check
  useEffect(() => {
    getSystemStatus().then(setSystemStatus).catch(console.error);
  }, []);

  // Analyze Video Pipeline Action
  const handleAnalyze = async () => {
    if (!url.trim()) return;
    setIsAnalyzing(true);
    setManualPrompt(null);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      const res = await analyzeVideo(url, settings);
      setActiveVideoId(res.video_id);
      setVideoTitle(res.title);
      setDurationSec(res.duration_sec);
      setClips(res.clips || []);
      if (res.clips && res.clips.length > 0) {
        setActiveClip(res.clips[0]);
        setSuccessMessage(`Analysis complete: ${res.clips.length} viral candidate clips ready.`);
      } else if (res.manual_prompt) {
        setSuccessMessage("Manual Gemini prompt compiled. Open 'Manual Gemini Web Mode' to copy.");
      }
      setManualPrompt(res.manual_prompt || null);

      // Set HTML5 video stream URL from static server mount
      setVideoSrc(`http://127.0.0.1:8000/cache/${res.video_id}/${res.video_id}.mp4`);

      // Load signal details if available
      const cached = await getCachedVideo(res.video_id);
      if (cached.video) {
        try {
          const rawHeatmap = JSON.parse(cached.video.heatmap_json || "[]");
          const rawAudio = JSON.parse(cached.video.audio_spikes_json || "[]");
          const rawVisual = JSON.parse(cached.video.visual_spikes_json || "[]");
          setHeatmap(rawHeatmap);
          setAudioSpikes(rawAudio);
          setVisualSpikes(rawVisual);
        } catch {
          // ignore parsing errors
        }
      }
    } catch (err: any) {
      console.error("Analysis failed", err);
      setErrorMessage(err.message || "Analysis request failed");
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Instant Smart Cache Reload
  const handleSelectCachedVideo = async (videoId: string) => {
    setErrorMessage(null);
    try {
      const res = await getCachedVideo(videoId);
      setActiveVideoId(videoId);
      setVideoTitle(res.video.title || videoId);
      setDurationSec(res.video.duration_sec || 0);
      setVideoSrc(`http://127.0.0.1:8000/cache/${videoId}/${videoId}.mp4`);
      setClips(res.clips || []);
      if (res.clips && res.clips.length > 0) {
        setActiveClip(res.clips[0]);
      }
      setSuccessMessage(`Loaded ${res.video.title || videoId} from Smart Cache (${res.clips.length} clips)`);
      try {
        setHeatmap(JSON.parse(res.video.heatmap_json || "[]"));
        setAudioSpikes(JSON.parse(res.video.audio_spikes_json || "[]"));
        setVisualSpikes(JSON.parse(res.video.visual_spikes_json || "[]"));
      } catch {
        // ignore
      }
    } catch (err: any) {
      console.error("Failed to load cached video", err);
      setErrorMessage(err.message || "Failed to load cached video");
    }
  };

  // Render Clip Action
  const handleRenderClip = async (clip: ClipCandidate) => {
    if (!activeVideoId) return;
    setRenderingClipId(clip.clip_id);
    setErrorMessage(null);
    try {
      const res = await renderClip(
        activeVideoId,
        clip.clip_id,
        settings,
        { clip_id: clip.clip_id, start_sec: clip.start_sec, end_sec: clip.end_sec },
        settings.custom_crop || undefined
      );

      // Update clip status in state
      setClips((prev) =>
        prev.map((c) =>
          c.clip_id === clip.clip_id
            ? {
                ...c,
                status: "completed",
                output_path_a: res.variant_a_path,
                output_path_b: res.variant_b_path || undefined,
                cover_path: res.cover_image_path,
              }
            : c
        )
      );
      setSuccessMessage(`Clip '${clip.title_hook}' rendered via ${res.encoder_used || "NVENC"}!`);
    } catch (err: any) {
      console.error("Render failed", err);
      setErrorMessage(err.message || "Render failed");
    } finally {
      setRenderingClipId(null);
    }
  };

  // Update Trim Boundaries
  const handleUpdateTrim = (clipId: string, startSec: number, endSec: number) => {
    setClips((prev) =>
      prev.map((c) =>
        c.clip_id === clipId ? { ...c, start_sec: startSec, end_sec: endSec } : c
      )
    );
    if (activeClip && activeClip.clip_id === clipId) {
      setActiveClip({ ...activeClip, start_sec: startSec, end_sec: endSec });
    }
  };

  return (
    <div className="min-h-screen flex flex-col pb-16">
      {/* Top Navigation */}
      <Header
        systemStatus={systemStatus}
        vramUsedMb={telemetry.vram_used_mb}
        vramTotalMb={telemetry.vram_total_mb}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenBatchQueue={() => setIsBatchOpen(true)}
        onOpenRetentionVault={() => setIsVaultOpen(true)}
        onOpenCache={() => setIsCacheOpen(true)}
        onOpenShortcuts={() => setIsShortcutsOpen(true)}
      />

      {/* Main Studio Viewport */}
      <main className="flex-1 max-w-[1600px] w-full mx-auto p-4 sm:p-6 space-y-6">
        {/* In-app Notification Banners */}
        {errorMessage && (
          <div className="flex items-center justify-between p-3 bg-studio-900 border border-tally-red/40 text-tally-red rounded text-xs font-mono">
            <div className="flex items-center gap-2.5">
              <AlertTriangle className="w-4 h-4 text-tally-red shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="p-1 hover:text-white rounded transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {successMessage && (
          <div className="flex items-center justify-between p-3 bg-studio-900 border border-tally-emerald/40 text-tally-emerald rounded text-xs font-mono">
            <div className="flex items-center gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-tally-emerald shrink-0" />
              <span>{successMessage}</span>
            </div>
            <button
              onClick={() => setSuccessMessage(null)}
              className="p-1 hover:text-white rounded transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* URL Input & Pipeline Controls */}
        <StudioWorkspace
          url={url}
          setUrl={setUrl}
          settings={settings}
          setSettings={setSettings}
          onAnalyze={handleAnalyze}
          isAnalyzing={isAnalyzing}
          manualPrompt={manualPrompt}
          videoId={activeVideoId}
          onManualClipsLoaded={(loadedClips) => {
            setClips(loadedClips);
            if (loadedClips.length > 0) setActiveClip(loadedClips[0]);
          }}
        />

        {/* Studio Dual-Pane: Heatmap Timeline + 9:16 Playground */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Pane (Timeline & Trimmer) */}
          <div className="lg:col-span-7 space-y-6">
            <HeatmapTimeline
              videoSrc={videoSrc}
              durationSec={durationSec}
              heatmap={heatmap}
              audioSpikes={audioSpikes}
              visualSpikes={visualSpikes}
              activeClip={activeClip}
              onUpdateTrim={handleUpdateTrim}
            />
          </div>

          {/* Right Pane (Live 9:16 Canvas & Caption Presets) */}
          <div className="lg:col-span-5 space-y-6">
            <LayoutCaptionPlayground
              activeClip={activeClip}
              captionTheme={settings.caption_theme}
              onChangeTheme={(theme) =>
                setSettings((prev) => ({ ...prev, caption_theme: theme }))
              }
              onUpdateCrop={(crop) =>
                setSettings((prev) => ({ ...prev, custom_crop: crop }))
              }
            />
          </div>
        </div>

        {/* Candidate Clips Grid */}
        <div className="space-y-4">
          <div className="flex items-center justify-between border-b border-studio-800 pb-2">
            <div className="flex items-center gap-2">
              <Film className="w-4 h-4 text-studio-400" />
              <h2 className="font-medium text-studio-100 text-sm tracking-tight">
                Candidate clips ({clips.length})
              </h2>
            </div>
            {clips.length > 0 && (
              <span className="text-xs font-mono text-studio-400">
                Ranked by multi-vector virality score
              </span>
            )}
          </div>

          {clips.length === 0 ? (
            <div className="p-12 text-center text-xs font-mono text-studio-500 bg-studio-900 border border-dashed border-studio-800 rounded">
              No candidate clips yet. Paste a YouTube URL above and click Analyze video.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {clips.map((clip, idx) => (
                <ClipCandidateCard
                  key={clip.clip_id || idx}
                  clip={clip}
                  index={idx}
                  isActive={activeClip?.clip_id === clip.clip_id}
                  onSelect={() => setActiveClip(clip)}
                  onRender={() => handleRenderClip(clip)}
                  onOpenUploadKit={() => setUploadKitClip(clip)}
                  isRendering={renderingClipId === clip.clip_id}
                />
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Sticky Bottom Telemetry Strip */}
      <TelemetryBar telemetry={telemetry} />

      {/* Modals & Slide-out Drawers */}
      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
      <BatchQueueModal isOpen={isBatchOpen} onClose={() => setIsBatchOpen(false)} settings={settings} />
      <RetentionVaultModal isOpen={isVaultOpen} onClose={() => setIsVaultOpen(false)} />
      <SmartCacheSidebar
        isOpen={isCacheOpen}
        onClose={() => setIsCacheOpen(false)}
        onSelectVideo={handleSelectCachedVideo}
      />
      <UploadKitDrawer
        clip={uploadKitClip}
        videoId={activeVideoId}
        onClose={() => setUploadKitClip(null)}
      />
      <KeyboardShortcutsModal
        isOpen={isShortcutsOpen}
        onClose={() => setIsShortcutsOpen(false)}
      />
    </div>
  );
}
