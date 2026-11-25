"use client";

import React, { useState } from "react";
import { Layout, Type, Sparkles, Layers, Sliders, Shield, Smartphone } from "lucide-react";
import { ClipCandidate, CropOverride } from "@/types";

interface LayoutCaptionPlaygroundProps {
  activeClip: ClipCandidate | null;
  captionTheme: "vice_city_neon" | "rockstar_bold" | "clean_minimal";
  onChangeTheme: (theme: "vice_city_neon" | "rockstar_bold" | "clean_minimal") => void;
  onUpdateCrop: (crop: CropOverride) => void;
}

type SafeZonePlatform = "none" | "shorts" | "tiktok" | "reels";

export const LayoutCaptionPlayground: React.FC<LayoutCaptionPlaygroundProps> = ({
  activeClip,
  captionTheme,
  onChangeTheme,
  onUpdateCrop,
}) => {
  const [layoutMode, setLayoutMode] = useState<"split" | "pure_916" | "blurred">("split");
  const [bannerVariant, setBannerVariant] = useState<"A" | "B">("A");
  const [safeZonePlatform, setSafeZonePlatform] = useState<SafeZonePlatform>("shorts");

  // Sample banner text
  const bannerTextA = activeClip?.top_banner_text_a || activeClip?.banner_text_a || "DID YOU SPOT THIS IN GTA 6?";
  const bannerTextB = activeClip?.top_banner_text_b || activeClip?.banner_text_b || "ROCKSTAR HID THIS IN TRAILER 1";
  const currentBanner = bannerVariant === "A" ? bannerTextA : bannerTextB;

  return (
    <div className="bg-studio-900 border border-studio-700/80 rounded-lg p-4 sm:p-5 flex flex-col gap-4 shadow-studio-card">
      <div className="flex items-center justify-between pb-3 border-b border-studio-800">
        <div>
          <h2 className="font-medium text-studio-100 text-sm tracking-tight flex items-center gap-2">
            <Layout className="w-4 h-4 text-studio-400" />
            <span>Vertical canvas & framing</span>
          </h2>
          <p className="text-[11px] text-studio-400 mt-0.5">Real-time 9:16 vertical composition and subtitle preview</p>
        </div>

        {/* Layout Mode Selector */}
        <div className="flex items-center gap-1 bg-studio-950 border border-studio-800 p-1 rounded-lg text-xs font-mono shadow-sm">
          <button
            onClick={() => setLayoutMode("split")}
            className={`px-2.5 py-1 rounded-md transition-all btn-tactile ${
              layoutMode === "split" ? "bg-studio-800 text-tally-amber font-medium shadow-studio-card" : "text-studio-400 hover:text-white"
            }`}
          >
            Split (35/65)
          </button>
          <button
            onClick={() => setLayoutMode("pure_916")}
            className={`px-2.5 py-1 rounded-md transition-all btn-tactile ${
              layoutMode === "pure_916" ? "bg-studio-800 text-tally-amber font-medium shadow-studio-card" : "text-studio-400 hover:text-white"
            }`}
          >
            Pure 9:16
          </button>
          <button
            onClick={() => setLayoutMode("blurred")}
            className={`px-2.5 py-1 rounded-md transition-all btn-tactile ${
              layoutMode === "blurred" ? "bg-studio-800 text-tally-amber font-medium shadow-studio-card" : "text-studio-400 hover:text-white"
            }`}
          >
            Blurred BG
          </button>
        </div>
      </div>

      <div className="flex flex-col md:flex-row items-center gap-6 justify-center">
        {/* 9:16 Phone Canvas Preview */}
        <div className="relative w-[240px] h-[426px] bg-studio-950 rounded-2xl overflow-hidden border border-studio-700 shadow-2xl flex flex-col select-none ring-1 ring-white/5">
          {/* Hardware Camera Viewport Framing Marks */}
          <div className="absolute top-2 left-2 text-[10px] text-studio-600/60 font-mono pointer-events-none select-none z-30">⌜</div>
          <div className="absolute top-2 right-2 text-[10px] text-studio-600/60 font-mono pointer-events-none select-none z-30">⌝</div>
          <div className="absolute bottom-2 left-2 text-[10px] text-studio-600/60 font-mono pointer-events-none select-none z-30">⌞</div>
          <div className="absolute bottom-2 right-2 text-[10px] text-studio-600/60 font-mono pointer-events-none select-none z-30">⌟</div>

          {/* Viewport Meta Bar */}
          <div className="absolute top-1.5 left-0 right-0 z-30 flex items-center justify-center pointer-events-none">
            <span className="text-[7.5px] font-mono text-studio-500/80 tracking-widest uppercase bg-studio-950/80 px-2 py-0.5 rounded-full border border-studio-800/60">
              9:16 • 1080x1920 • 60FPS NVENC
            </span>
          </div>

          {/* Top 3s Curiosity Banner Overlay */}
          <div className="absolute top-7 left-3 right-3 z-30">
            <div
              className={`p-2 rounded-lg text-center text-[10px] font-mono font-medium tracking-wide shadow-md transition-all ${
                captionTheme === "vice_city_neon"
                  ? "bg-studio-800/95 text-tally-amber border border-tally-amber/40 shadow-studio-card"
                  : captionTheme === "rockstar_bold"
                  ? "bg-studio-800/95 text-studio-100 border border-studio-600 font-bold"
                  : "bg-studio-900/90 text-studio-300 border border-studio-750"
              }`}
            >
              <div className="flex items-center justify-center gap-1.5 mb-0.5 text-[8px] opacity-75">
                <span className="w-1.5 h-1.5 rounded-full bg-tally-amber animate-pulse" />
                <span>HOOK TALLY 00:03.00</span>
              </div>
              {currentBanner}
            </div>
          </div>

          {/* Canvas Framing Body */}
          {layoutMode === "split" ? (
            <>
              {/* Top 35% Facecam Region */}
              <div className="relative h-[35%] bg-studio-850 border-b border-studio-700/80 flex items-center justify-center overflow-hidden">
                <div className="text-[11px] font-mono text-studio-300 flex flex-col items-center gap-0.5">
                  <span className="font-medium">Facecam (top 35%)</span>
                  <span className="text-[9px] text-studio-500">Auto-tracked crop</span>
                </div>
              </div>

              {/* Bottom 65% Gameplay Region */}
              <div className="relative h-[65%] bg-studio-900 flex items-center justify-center overflow-hidden">
                <div className="text-[11px] font-mono text-studio-300 flex flex-col items-center gap-0.5">
                  <span className="font-medium">Gameplay (bottom 65%)</span>
                  <span className="text-[9px] text-studio-500">Center-tracked action</span>
                </div>
              </div>
            </>
          ) : layoutMode === "blurred" ? (
            <div className="relative w-full h-full bg-studio-900 flex items-center justify-center p-2">
              <div className="w-full aspect-video bg-studio-800 border border-studio-700 rounded flex items-center justify-center text-[11px] font-mono text-studio-200">
                16:9 Inset frame
              </div>
            </div>
          ) : (
            <div className="relative w-full h-full bg-studio-900 flex items-center justify-center">
              <div className="text-[11px] font-mono text-studio-300 flex flex-col items-center gap-0.5">
                <span className="font-medium">Pure 9:16 crop</span>
                <span className="text-[9px] text-studio-500">Centered 1080x1920</span>
              </div>
            </div>
          )}

          {/* Dynamic Caption Bursts in Lower Third */}
          <div className="absolute bottom-16 left-3 right-3 z-30 flex flex-col items-center pointer-events-none">
            <div className="text-center font-medium text-xs tracking-wide">
              {captionTheme === "vice_city_neon" && (
                <div className="bg-black/75 px-3 py-1 rounded text-studio-200 font-mono border border-studio-700">
                  LOOK WHAT <span className="text-tally-amber font-bold">HAPPENS</span> NEXT
                </div>
              )}
              {captionTheme === "rockstar_bold" && (
                <div className="bg-black/80 px-3 py-1 rounded font-mono text-studio-100 font-bold border border-studio-600">
                  LOOK WHAT <span className="text-tally-amber underline">HAPPENS</span> NEXT
                </div>
              )}
              {captionTheme === "clean_minimal" && (
                <div className="text-studio-200 bg-studio-950/80 px-3 py-1 rounded border border-studio-800">
                  Look what <span className="text-studio-100 font-medium">happens</span> next
                </div>
              )}
            </div>
          </div>

          {/* Platform Safe Zone Guide Overlay */}
          {safeZonePlatform !== "none" && (
            <div className="absolute inset-0 z-25 pointer-events-none select-none">
              {/* Header UI Area */}
              <div
                className={`absolute top-0 left-0 right-0 border-b border-dashed border-red-400/40 bg-red-950/20 flex items-center justify-between px-3 text-[8px] font-mono text-red-300/80 ${
                  safeZonePlatform === "tiktok" ? "h-[14%]" : safeZonePlatform === "shorts" ? "h-[12%]" : "h-[10%]"
                }`}
              >
                <span>Header UI</span>
                <span className="uppercase">{safeZonePlatform}</span>
              </div>

              {/* Right-Rail Engagement Buttons (Like, Share, Comment) */}
              <div
                className={`absolute right-0 border-l border-dashed border-red-400/40 bg-red-950/20 flex flex-col items-center justify-center gap-2 text-[8px] font-mono text-red-300/90 py-2 ${
                  safeZonePlatform === "tiktok"
                    ? "top-[32%] bottom-[22%] w-[46px]"
                    : safeZonePlatform === "shorts"
                    ? "top-[38%] bottom-[16%] w-[42px]"
                    : "top-[42%] bottom-[18%] w-[40px]"
                }`}
              >
                <div className="w-4 h-4 rounded-full border border-red-400/50 flex items-center justify-center text-[7px]">❤️</div>
                <div className="w-4 h-4 rounded-full border border-red-400/50 flex items-center justify-center text-[7px]">💬</div>
                <div className="w-4 h-4 rounded-full border border-red-400/50 flex items-center justify-center text-[7px]">↗️</div>
                <span className="text-[7px] rotate-90 tracking-tighter opacity-70">UI RAIL</span>
              </div>

              {/* Bottom Metadata & Captions Danger Zone */}
              <div
                className={`absolute bottom-0 left-0 right-0 border-t border-dashed border-red-400/40 bg-red-950/20 flex items-center justify-between px-3 text-[8px] font-mono text-red-300/80 ${
                  safeZonePlatform === "tiktok" ? "h-[22%]" : safeZonePlatform === "shorts" ? "h-[16%]" : "h-[18%]"
                }`}
              >
                <span>@creator & audio ticker</span>
                <span className="text-[7px] text-red-400/80">AVOID SUBTITLES</span>
              </div>

              {/* Center Safe Canvas Rect */}
              <div
                className="absolute border border-dashed border-tally-emerald/40 pointer-events-none rounded"
                style={{
                  top: safeZonePlatform === "tiktok" ? "14%" : safeZonePlatform === "shorts" ? "12%" : "10%",
                  bottom: safeZonePlatform === "tiktok" ? "22%" : safeZonePlatform === "shorts" ? "16%" : "18%",
                  left: "8px",
                  right: safeZonePlatform === "tiktok" ? "50px" : safeZonePlatform === "shorts" ? "46px" : "44px",
                }}
              >
                <span className="absolute top-1 left-1.5 text-[7px] font-mono text-tally-emerald/80 font-medium">
                  SAFE CONTENT AREA
                </span>
              </div>
            </div>
          )}

          {/* Simulated Controls Strip fallback when safe-zone off */}
          {safeZonePlatform === "none" && (
            <div className="absolute right-2 bottom-8 z-20 flex flex-col gap-2 items-center opacity-30">
              <div className="w-4 h-4 rounded-full bg-white/30" />
              <div className="w-4 h-4 rounded-full bg-white/30" />
              <div className="w-4 h-4 rounded-full bg-white/30" />
            </div>
          )}
        </div>

        {/* Playground Controls Side Panel */}
        <div className="flex-1 max-w-sm flex flex-col gap-4">
          {/* Platform Safe Zone Preview Selector */}
          <div className="bg-studio-950 border border-studio-800 p-3.5 rounded">
            <div className="text-xs font-mono text-studio-400 mb-2 flex items-center justify-between font-medium">
              <span className="flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-studio-400" />
                <span>Safe zone preview</span>
              </span>
              {safeZonePlatform !== "none" ? (
                <span className="text-[10px] font-mono text-tally-emerald bg-tally-emerald/10 border border-tally-emerald/30 px-1.5 py-0.5 rounded">
                  Active
                </span>
              ) : (
                <span className="text-[10px] font-mono text-studio-500">Off</span>
              )}
            </div>
            <div className="grid grid-cols-4 gap-1.5">
              {(
                [
                  { id: "none", label: "Off" },
                  { id: "shorts", label: "Shorts" },
                  { id: "tiktok", label: "TikTok" },
                  { id: "reels", label: "Reels" },
                ] as const
              ).map((plat) => (
                <button
                  key={plat.id}
                  onClick={() => setSafeZonePlatform(plat.id)}
                  className={`py-1.5 px-1.5 rounded-md text-xs font-mono border transition-all text-center btn-tactile ${
                    safeZonePlatform === plat.id
                      ? "bg-studio-800 border-tally-amber text-tally-amber font-medium ring-1 ring-tally-amber/30 shadow-studio-card"
                      : "bg-studio-900 border-studio-800 text-studio-400 hover:text-white"
                  }`}
                >
                  {plat.label}
                </button>
              ))}
            </div>
            <p className="text-[10px] font-mono text-studio-500 mt-2">
              Prevents captions & hooks from being obscured by UI buttons or title bars.
            </p>
          </div>
          {/* Caption Theme Switcher */}
          <div className="bg-studio-950 border border-studio-800 p-3.5 rounded-lg shadow-sm">
            <div className="text-xs font-mono text-studio-400 mb-2.5 flex items-center gap-1.5 font-medium">
              <Type className="w-3.5 h-3.5 text-studio-500" />
              <span>Caption preset</span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <button
                onClick={() => onChangeTheme("vice_city_neon")}
                className={`p-2 rounded-md text-xs font-mono border transition-all text-center btn-tactile ${
                  captionTheme === "vice_city_neon"
                    ? "bg-studio-800 border-tally-amber text-tally-amber font-medium ring-1 ring-tally-amber/30 shadow-studio-card"
                    : "bg-studio-900 border-studio-800 text-studio-400 hover:text-white"
                }`}
              >
                Vice Neon
              </button>
              <button
                onClick={() => onChangeTheme("rockstar_bold")}
                className={`p-2 rounded-md text-xs font-mono border transition-all text-center btn-tactile ${
                  captionTheme === "rockstar_bold"
                    ? "bg-studio-800 border-tally-amber text-tally-amber font-medium ring-1 ring-tally-amber/30 shadow-studio-card"
                    : "bg-studio-900 border-studio-800 text-studio-400 hover:text-white"
                }`}
              >
                Rockstar Bold
              </button>
              <button
                onClick={() => onChangeTheme("clean_minimal")}
                className={`p-2 rounded-md text-xs font-mono border transition-all text-center btn-tactile ${
                  captionTheme === "clean_minimal"
                    ? "bg-studio-800 border-tally-amber text-tally-amber font-medium ring-1 ring-tally-amber/30 shadow-studio-card"
                    : "bg-studio-900 border-studio-800 text-studio-400 hover:text-white"
                }`}
              >
                Clean Minimal
              </button>
            </div>
          </div>

          {/* Curiosity Banner Variant Switcher */}
          <div className="bg-studio-950 border border-studio-800 p-3.5 rounded-lg shadow-sm">
            <div className="text-xs font-mono text-studio-400 mb-2.5 flex items-center justify-between font-medium">
              <span className="flex items-center gap-1.5">
                <Layout className="w-3.5 h-3.5 text-studio-500" />
                <span>3s hook banner</span>
              </span>
              <div className="flex gap-1.5">
                <button
                  onClick={() => setBannerVariant("A")}
                  className={`px-2.5 py-0.5 rounded-md text-[10px] font-mono transition-all btn-tactile ${
                    bannerVariant === "A"
                      ? "bg-studio-800 text-tally-amber border border-tally-amber/40 font-medium shadow-studio-card"
                      : "bg-studio-900 text-studio-400 border border-studio-800"
                  }`}
                >
                  Variant A
                </button>
                <button
                  onClick={() => setBannerVariant("B")}
                  className={`px-2.5 py-0.5 rounded-md text-[10px] font-mono transition-all btn-tactile ${
                    bannerVariant === "B"
                      ? "bg-studio-800 text-tally-amber border border-tally-amber/40 font-medium shadow-studio-card"
                      : "bg-studio-900 text-studio-400 border border-studio-800"
                  }`}
                >
                  Variant B
                </button>
              </div>
            </div>
            <div className="p-2.5 bg-studio-900 border border-studio-800 rounded text-xs font-mono text-studio-200">
              {currentBanner}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
