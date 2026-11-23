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
    <div className="bg-[#121218] border border-[#262636] rounded-xl p-4 sm:p-5 flex flex-col gap-4 shadow-studio-glow">
      <div className="flex items-center justify-between pb-3 border-b border-[#1E1E2A]">
        <div>
          <h2 className="font-bold text-white text-sm tracking-tight flex items-center gap-2">
            <Layout className="w-4 h-4 text-[#00F0FF]" />
            <span>LIVE 9:16 LAYOUT & CAPTION PLAYGROUND</span>
          </h2>
          <p className="text-[11px] text-[#7E7E9A]">Real-time vertical canvas framing and subtitle preview</p>
        </div>

        {/* Layout Mode Selector */}
        <div className="flex items-center gap-1 bg-[#0A0A0F] border border-[#262636] p-1 rounded-lg text-xs font-mono">
          <button
            onClick={() => setLayoutMode("split")}
            className={`px-2 py-1 rounded transition-colors ${
              layoutMode === "split" ? "bg-[#1A1A24] text-[#00F0FF] font-bold" : "text-[#7E7E9A] hover:text-white"
            }`}
          >
            Split (35/65)
          </button>
          <button
            onClick={() => setLayoutMode("pure_916")}
            className={`px-2 py-1 rounded transition-colors ${
              layoutMode === "pure_916" ? "bg-[#1A1A24] text-[#00F0FF] font-bold" : "text-[#7E7E9A] hover:text-white"
            }`}
          >
            Pure 9:16
          </button>
          <button
            onClick={() => setLayoutMode("blurred")}
            className={`px-2 py-1 rounded transition-colors ${
              layoutMode === "blurred" ? "bg-[#1A1A24] text-[#00F0FF] font-bold" : "text-[#7E7E9A] hover:text-white"
            }`}
          >
            Blurred BG
          </button>
        </div>
      </div>

      <div className="flex flex-col md:flex-row items-center gap-6 justify-center">
        {/* 9:16 Phone Canvas Preview */}
        <div className="relative w-[240px] h-[426px] bg-black rounded-2xl overflow-hidden border-2 border-[#262636] shadow-2xl flex flex-col select-none">
          {/* Top 3s Curiosity Banner Overlay */}
          <div className="absolute top-6 left-3 right-3 z-30 animate-pulse-subtle">
            <div
              className={`p-2 rounded text-center text-[10px] font-black tracking-wider uppercase shadow-lg ${
                captionTheme === "vice_city_neon"
                  ? "bg-[#FF2E93] text-white shadow-neon-pink"
                  : captionTheme === "rockstar_bold"
                  ? "bg-[#FFE600] text-black shadow-neon-yellow"
                  : "bg-[#1A1A24] text-[#00F0FF] border border-[#00F0FF]/40"
              }`}
            >
              {currentBanner}
            </div>
          </div>

          {/* Canvas Framing Body */}
          {layoutMode === "split" ? (
            <>
              {/* Top 35% Facecam Region */}
              <div className="relative h-[35%] bg-[#1A1A24] border-b-2 border-[#00F0FF]/40 flex items-center justify-center overflow-hidden">
                <div className="text-[11px] font-mono text-[#00F0FF] flex flex-col items-center gap-1">
                  <span className="font-bold">FACECAM (TOP 35%)</span>
                  <span className="text-[9px] text-[#7E7E9A]">MediaPipe Auto-Tracked</span>
                </div>
              </div>

              {/* Bottom 65% Gameplay Region */}
              <div className="relative h-[65%] bg-[#0A0A0F] flex items-center justify-center overflow-hidden">
                <div className="text-[11px] font-mono text-[#FF2E93] flex flex-col items-center gap-1">
                  <span className="font-bold">GAMEPLAY (BOTTOM 65%)</span>
                  <span className="text-[9px] text-[#7E7E9A]">Center-Tracked Action</span>
                </div>
              </div>
            </>
          ) : layoutMode === "blurred" ? (
            <div className="relative w-full h-full bg-[#121218] flex items-center justify-center p-2">
              <div className="w-full aspect-video bg-[#1A1A24] border border-[#262636] rounded flex items-center justify-center text-[11px] font-mono text-white">
                16:9 Inset Frame
              </div>
            </div>
          ) : (
            <div className="relative w-full h-full bg-[#0A0A0F] flex items-center justify-center">
              <div className="text-[11px] font-mono text-[#00F0FF] flex flex-col items-center gap-1">
                <span className="font-bold">PURE 9:16 CROP</span>
                <span className="text-[9px] text-[#7E7E9A]">Action-Centered 1080x1920</span>
              </div>
            </div>
          )}

          {/* Dynamic Caption Bursts in Lower Third */}
          <div className="absolute bottom-16 left-3 right-3 z-30 flex flex-col items-center pointer-events-none">
            <div className="text-center font-black uppercase text-xs tracking-wide">
              {captionTheme === "vice_city_neon" && (
                <div className="drop-shadow-[0_2px_4px_rgba(0,0,0,0.9)]">
                  <span className="text-[#00F0FF]">LOOK WHAT </span>
                  <span className="text-[#FF2E93] text-sm scale-110 inline-block text-neon-pink">
                    HAPPENS
                  </span>
                  <span className="text-[#00F0FF]"> NEXT</span>
                </div>
              )}
              {captionTheme === "rockstar_bold" && (
                <div className="font-mono text-[#FFE600] drop-shadow-[0_2px_2px_rgba(0,0,0,1)]">
                  LOOK WHAT <span className="text-white text-sm underline">HAPPENS</span> NEXT
                </div>
              )}
              {captionTheme === "clean_minimal" && (
                <div className="text-white bg-black/60 px-3 py-1 rounded-full backdrop-blur-sm border border-white/10">
                  Look what <span className="text-[#00F0FF]">happens</span> next
                </div>
              )}
            </div>
          </div>

          {/* TikTok / Shorts UI Simulation Strip */}
          <div className="absolute right-2 bottom-8 z-20 flex flex-col gap-2 items-center opacity-40">
            <div className="w-5 h-5 rounded-full bg-white/20" />
            <div className="w-5 h-5 rounded-full bg-white/20" />
            <div className="w-5 h-5 rounded-full bg-white/20" />
          </div>
        </div>

        {/* Playground Controls Side Panel */}
        <div className="flex-1 max-w-sm flex flex-col gap-4">
          {/* Caption Theme Switcher */}
          <div className="bg-[#0A0A0F] border border-[#262636] p-3 rounded-lg">
            <div className="text-xs font-mono text-[#7E7E9A] mb-2 flex items-center gap-1.5">
              <Type className="w-3.5 h-3.5 text-[#00F0FF]" />
              <span>CAPTION THEME PRESET:</span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <button
                onClick={() => onChangeTheme("vice_city_neon")}
                className={`p-2 rounded text-xs font-mono border transition-all text-center ${
                  captionTheme === "vice_city_neon"
                    ? "bg-[#FF2E93]/20 border-[#FF2E93] text-[#FF2E93] font-bold shadow-neon-pink"
                    : "bg-[#121218] border-[#262636] text-[#7E7E9A] hover:text-white"
                }`}
              >
                Vice Neon
              </button>
              <button
                onClick={() => onChangeTheme("rockstar_bold")}
                className={`p-2 rounded text-xs font-mono border transition-all text-center ${
                  captionTheme === "rockstar_bold"
                    ? "bg-[#FFE600]/20 border-[#FFE600] text-[#FFE600] font-bold shadow-neon-yellow"
                    : "bg-[#121218] border-[#262636] text-[#7E7E9A] hover:text-white"
                }`}
              >
                Rockstar Bold
              </button>
              <button
                onClick={() => onChangeTheme("clean_minimal")}
                className={`p-2 rounded text-xs font-mono border transition-all text-center ${
                  captionTheme === "clean_minimal"
                    ? "bg-[#00F0FF]/20 border-[#00F0FF] text-[#00F0FF] font-bold shadow-neon-cyan"
                    : "bg-[#121218] border-[#262636] text-[#7E7E9A] hover:text-white"
                }`}
              >
                Clean Minimal
              </button>
            </div>
          </div>

          {/* Curiosity Banner Variant Switcher */}
          <div className="bg-[#0A0A0F] border border-[#262636] p-3 rounded-lg">
            <div className="text-xs font-mono text-[#7E7E9A] mb-2 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-[#FF2E93]" />
                <span>3s HOOK BANNER PREVIEW:</span>
              </span>
              <div className="flex gap-1">
                <button
                  onClick={() => setBannerVariant("A")}
                  className={`px-2 py-0.5 rounded text-[10px] font-mono ${
                    bannerVariant === "A" ? "bg-[#FF2E93] text-black font-bold" : "bg-[#1A1A24] text-[#7E7E9A]"
                  }`}
                >
                  Variant A
                </button>
                <button
                  onClick={() => setBannerVariant("B")}
                  className={`px-2 py-0.5 rounded text-[10px] font-mono ${
                    bannerVariant === "B" ? "bg-[#00F0FF] text-black font-bold" : "bg-[#1A1A24] text-[#7E7E9A]"
                  }`}
                >
                  Variant B
                </button>
              </div>
            </div>
            <div className="p-2 bg-[#121218] border border-[#262636] rounded text-xs font-mono text-white">
              {currentBanner}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
