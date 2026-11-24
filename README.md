# 🎬 VICECLIP STUDIO — GTA 6 Edition
### Local-First AI Viral Video Clipping Studio for YouTube Shorts & TikTok

> **Outperform OpusClip with zero monthly subscriptions, zero cloud queue times, and 100% hardware-accelerated local rendering on your own PC.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-viceclip--studio.vercel.app-00F0FF?style=flat&logo=vercel&logoColor=white)](https://viceclip-studio.vercel.app/)
[![Python: 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![CUDA: 12.4](https://img.shields.io/badge/CUDA-12.4-76B900?logo=nvidia&logoColor=white)](https://developer.nvidia.com/cuda-toolkit)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.6.0%2Bcu124-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Next.js: 14](https://img.shields.io/badge/Next.js-14.2-black?logo=next.js&logoColor=white)](https://nextjs.org/)
[![FFmpeg: 9.1 NVENC](https://img.shields.io/badge/FFmpeg-NVENC%2060fps-007808?logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

---

## ⚡ The Problem: Why ViceClip Studio?

Most cloud-based AI clippers (such as OpusClip, Klap, or Munch) charge **$20 to $50 per month**, force your video uploads through slow server queues, ruin gaming layouts with generic center crops, and burn in cookie-cutter captions with zero audience engagement intelligence.

**ViceClip Studio** is built from the ground up as a **local-first, hardware-accelerated AI production pipeline**:
- **$0.00 Running Cost:** Runs locally on your own GPU. No cloud render bills.
- **Hardware-Accelerated 60 FPS Export:** Utilizes NVIDIA NVENC (`h264_nvenc`) to render full 1080x1920 60fps Shorts in **under 25 seconds** (tested on RTX 3050 Laptop GPU).
- **Multi-Modal Signal Convergence:** Combines YouTube Most-Replayed Heatmaps, Librosa audio dB spikes, and OpenCV visual motion vectors to pinpoint viral moments where action and audience interest peak simultaneously.
- **Smart Gaming Layouts:** Detects streamer facecams and gameplay separately, framing them automatically for 9:16 vertical viewports without manual keyframing.
- **Viral 4-Vector AI Scoring:** Evaluates clips across **Visual Hook (3s)**, **Infinite Replay Loop**, **Debate Bait**, and **Payoff Speed**.
- **1-Click Upload Kit:** Generates 3 A/B test viral titles, high-relevance hashtags, a debate-sparking pinned comment, and extracts a high-contrast cover thumbnail for YouTube Shorts.

---

## 🏗️ System Architecture

```
[ Long-form YouTube Video / Local MP4 ]
                    │
                    ▼
┌──────────────────────────────────────────────────────────┐
│  PASS 1: MULTI-MODAL SIGNAL INGESTION                    │
│  • yt-dlp Video & Audio Stream Extraction                │
│  • Faster-Whisper CUDA Word-Level Timestamps             │
│  • Librosa Audio dB Transient / Excitement Detection     │
│  • OpenCV Optical Flow & Visual Intensity Vectoring      │
│  • YouTube Most-Replayed Heatmap Normalization           │
└───────────────────────────┬──────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────┐
│  PASS 2: VIRAL BRAIN & CANDIDATE REASONING               │
│  • Online: Google Gemini 3.5 Flash Reasoning             │
│  • Offline / Free: Multi-Signal Convergence Fallback     │
│  • Retention Vault Pattern Matching & Infinite Loop Trim │
│  • Candidate Generation (5-8 ranked clips with A/B hooks)│
└───────────────────────────┬──────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────┐
│  PASS 3: SMART FRAMING & STYLING                         │
│  • Lossless Keyframe Slicing with Pre-Roll Buffer        │
│  • Facecam Detection (MediaPipe / Haar Cascade)          │
│  • Animated ASS Subtitles (Neon Glow, Karaoke Pop)       │
│  • 3-Second Top Curiosity Banner Variants (A & B)        │
│  • Optional: Transformative Commentary Voiceover (TTS)   │
│  • Optional: Dead-Air Silence Trimmer                    │
└───────────────────────────┬──────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────┐
│  PASS 4: NVENC HARDWARE GPU EXPORT                       │
│  • NVIDIA NVENC (h264_nvenc) 1080x1920 @ 60fps (~20s)   │
│  • Variant A & Variant B Exports (Different Curiosities) │
│  • High-Contrast Shorts Cover Frame PNG Extraction       │
│  • 1-Click Upload Kit (Titles, Hashtags, Pinned Comment) │
└──────────────────────────────────────────────────────────┘
```

---

## 💻 Hardware Requirements

| Component | Minimum | Recommended |
| :--- | :--- | :--- |
| **OS** | Windows 10 / 11 (64-bit) | Windows 11 (64-bit) |
| **GPU** | CPU Only (Software x264) | **NVIDIA RTX 3050 (6GB VRAM)** or higher |
| **VRAM** | 4 GB | 6 GB hard ceiling (Sequential VRAM management) |
| **RAM** | 8 GB | 16 GB DDR4/DDR5 |
| **Python** | Python 3.11+ | Python 3.12 |
| **Node.js** | Node.js 18+ | Node.js 20+ |
| **FFmpeg** | FFmpeg 6.0+ | **FFmpeg 9.1 (Gyan Build)** with NVENC |

---

## 🚀 Quick Start: Run On Your Own PC (3 Steps)

### Step 1: Clone the Repository
```bash
git clone https://github.com/smukulsaini369090-hub/viceclip-studio.git
cd viceclip-studio
```

### Step 2: Run the 1-Click Installer
Double-click `setup.bat` (or run PowerShell):
```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1
```
*What this does automatically:*
- Initializes an isolated Python virtual environment (`.venv`).
- Auto-detects your NVIDIA GPU and installs PyTorch with CUDA 12.4 acceleration.
- Installs backend requirements (`faster-whisper`, `fastapi`, `uvicorn`, `librosa`, etc.).
- Verifies FFmpeg and NVENC hardware encoder readiness.
- Installs Next.js frontend dependencies via `npm install`.
- Generates default audio SFX and synthwave music loops.

> **Tip (FFmpeg):** If you don't have FFmpeg installed, run this in PowerShell:
> ```powershell
> winget install Gyan.FFmpeg
> ```

### Step 3: Launch ViceClip Studio
Double-click `start.bat` (or `start_viceclip.bat`):
```cmd
start.bat
```
Both the FastAPI backend (`http://127.0.0.1:8000`) and the Next.js Studio frontend (`http://localhost:3000`) will boot up and automatically open in your default browser.

---

## 🔑 AI Modes: Free vs API

ViceClip Studio supports two operational modes:

### 1. 100% Free Offline Heuristic Mode (No API Key Required)
Leave `GEMINI_API_KEY=` blank in `.env`.
The pipeline uses its built-in **Multi-Modal Signal Convergence Engine** to detect viral peaks directly from audio spikes, video motion, and YouTube audience retention heatmaps.

### 2. Auto Gemini Viral Brain Mode (Recommended)
Get a free API key from [Google AI Studio](https://aistudio.google.com/) and paste it into `.env`:
```env
GEMINI_API_KEY=AIzaSy...
GEMINI_FAST_MODEL=gemini-3.5-flash-lite
GEMINI_DEEP_MODEL=gemini-3.5-flash-lite
```
The Viral Brain will score and rank candidate clips with deep semantic reasoning, generating high-conversion title hooks and curiosity banners.

---



## 📁 Project Structure

```
ViceClip-Studio/
├── backend/
│   ├── app/
│   │   ├── api/               # FastAPI endpoints (analysis, render, batch, vault, telemetry)
│   │   ├── core/              # AI engines (Whisper, Gemini Brain, Heuristics, NVENC Renderer)
│   │   ├── db/                # Async SQLite Smart Cache & Models
│   │   ├── services/          # Multi-stage rendering pipeline & batch worker
│   │   ├── config.py          # Dynamic hardware & path resolution
│   │   └── main.py            # FastAPI application factory
│   └── scripts/
│       ├── smoke_test.py      # Diagnostic hardware & NVENC verification suite
│       └── verify_api.py      # Automated contract & endpoint audit
├── frontend/
│   ├── src/
│   │   ├── app/               # Next.js 14 App Router (Studio UI & layouts)
│   │   ├── components/        # Interactive components (Canvas, Cards, Drawers, Modals)
│   │   └── lib/               # Typed API client & telemetry SSE hooks
│   └── package.json
├── assets/                    # Royalty-free SFX & synthwave background music loops
├── setup.bat                  # 1-click Windows installer
├── setup.ps1                  # PowerShell installation logic
├── start.bat                  # 1-click studio launcher
├── .env.example               # Environment variables template
└── .gitignore                 # GitHub-safe repository exclusions
```

---
https://viceclip-studio.vercel.app/  

## 🛡️ License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

## ⭐ Star the Project
If you find ViceClip Studio useful for your content creation workflow or development portfolio, please give the repository a **Star** on GitHub!
