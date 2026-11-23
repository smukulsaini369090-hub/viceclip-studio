"use client";

import React, { useState } from "react";
import { Layout, Type, Sparkles, Layers, Sliders } from "lucide-react";
import { ClipCandidate, CropOverride } from "@/types";

interface LayoutCaptionPlaygroundProps {
  activeClip: ClipCandidate | null;
  captionTheme: "vice_city_neon" | "rockstar_bold" | "clean_minimal";
  onChangeTheme: (theme: "vice_city_neon" | "rockstar_bold" | "clean_minimal") => void;
  onUpdateCrop: (crop: CropOverride) => void;
}

export const LayoutCaptionPlayground: React.FC<LayoutCaptionPlaygroundProps> = ({
  activeClip,
  captionTheme,
  onChangeTheme,
  onUpdateCrop,
}) => {
  const [layoutMode, setLayoutMode] = useState<"split" | "pure_916" | "blurred">("split");
  const [bannerVariant, setBannerVariant] = useState<"A" | "B">("A");

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
        <div className="flex items-center gap-1 bg-studio-950 border border-studio-800 p-1 rounded text-xs font-mono">
          <button
            onClick={() => setLayoutMode("split")}
            className={`px-2.5 py-1 rounded transition-colors ${
              layoutMode === "split" ? "bg-studio-800 text-tally-amber font-medium" : "text-studio-400 hover:text-white"
            }`}
          >
            Split (35/65)
          </button>
          <button
            onClick={() => setLayoutMode("pure_916")}
            className={`px-2.5 py-1 rounded transition-colors ${
              layoutMode === "pure_916" ? "bg-studio-800 text-tally-amber font-medium" : "text-studio-400 hover:text-white"
            }`}
          >
            Pure 9:16
          </button>
          <button
            onClick={() => setLayoutMode("blurred")}
            className={`px-2.5 py-1 rounded transition-colors ${
              layoutMode === "blurred" ? "bg-studio-800 text-tally-amber font-medium" : "text-studio-400 hover:text-white"
            }`}
          >
            Blurred BG
          </button>
        </div>
      </div>

      <div className="flex flex-col md:flex-row items-center gap-6 justify-center">
        {/* 9:16 Phone Canvas Preview */}
        <div className="relative w-[240px] h-[426px] bg-studio-950 rounded-xl overflow-hidden border border-studio-700 shadow-2xl flex flex-col select-none">
          {/* Top 3s Curiosity Banner Overlay */}
          <div className="absolute top-5 left-3 right-3 z-30">
            <div
              className={`p-2 rounded text-center text-[10px] font-mono font-medium tracking-wide shadow-md ${
                captionTheme === "vice_city_neon"
                  ? "bg-studio-800 text-tally-amber border border-tally-amber/40"
                  : captionTheme === "rockstar_bold"
                  ? "bg-studio-800 text-studio-100 border border-studio-600 font-bold"
                  : "bg-studio-900/90 text-studio-300 border border-studio-750"
              }`}
            >
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

          {/* Simulated Controls Strip */}
          <div className="absolute right-2 bottom-8 z-20 flex flex-col gap-2 items-center opacity-30">
            <div className="w-4 h-4 rounded-full bg-white/30" />
            <div className="w-4 h-4 rounded-full bg-white/30" />
            <div className="w-4 h-4 rounded-full bg-white/30" />
          </div>
        </div>

        {/* Playground Controls Side Panel */}
        <div className="flex-1 max-w-sm flex flex-col gap-4">
          {/* Caption Theme Switcher */}
          <div className="bg-studio-950 border border-studio-800 p-3.5 rounded">
            <div className="text-xs font-mono text-studio-400 mb-2.5 flex items-center gap-1.5 font-medium">
              <Type className="w-3.5 h-3.5 text-studio-500" />
              <span>Caption preset</span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <button
                onClick={() => onChangeTheme("vice_city_neon")}
                className={`p-2 rounded text-xs font-mono border transition-colors text-center ${
                  captionTheme === "vice_city_neon"
                    ? "bg-studio-800 border-tally-amber text-tally-amber font-medium ring-1 ring-tally-amber/30"
                    : "bg-studio-900 border-studio-800 text-studio-400 hover:text-white"
                }`}
              >
                Vice Neon
              </button>
              <button
                onClick={() => onChangeTheme("rockstar_bold")}
                className={`p-2 rounded text-xs font-mono border transition-colors text-center ${
                  captionTheme === "rockstar_bold"
                    ? "bg-studio-800 border-tally-amber text-tally-amber font-medium ring-1 ring-tally-amber/30"
                    : "bg-studio-900 border-studio-800 text-studio-400 hover:text-white"
                }`}
              >
                Rockstar Bold
              </button>
              <button
                onClick={() => onChangeTheme("clean_minimal")}
                className={`p-2 rounded text-xs font-mono border transition-colors text-center ${
                  captionTheme === "clean_minimal"
                    ? "bg-studio-800 border-tally-amber text-tally-amber font-medium ring-1 ring-tally-amber/30"
                    : "bg-studio-900 border-studio-800 text-studio-400 hover:text-white"
                }`}
              >
                Clean Minimal
              </button>
            </div>
          </div>

          {/* Curiosity Banner Variant Switcher */}
          <div className="bg-studio-950 border border-studio-800 p-3.5 rounded">
            <div className="text-xs font-mono text-studio-400 mb-2.5 flex items-center justify-between font-medium">
              <span className="flex items-center gap-1.5">
                <Layout className="w-3.5 h-3.5 text-studio-500" />
                <span>3s hook banner</span>
              </span>
              <div className="flex gap-1.5">
                <button
                  onClick={() => setBannerVariant("A")}
                  className={`px-2 py-0.5 rounded text-[10px] font-mono transition-colors ${
                    bannerVariant === "A"
                      ? "bg-studio-800 text-tally-amber border border-tally-amber/40 font-medium"
                      : "bg-studio-900 text-studio-400 border border-studio-800"
                  }`}
                >
                  Variant A
                </button>
                <button
                  onClick={() => setBannerVariant("B")}
                  className={`px-2 py-0.5 rounded text-[10px] font-mono transition-colors ${
                    bannerVariant === "B"
                      ? "bg-studio-800 text-tally-amber border border-tally-amber/40 font-medium"
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
