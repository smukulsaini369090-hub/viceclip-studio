import {
  BatchJob,
  CachedVideo,
  ClipCandidate,
  CropOverride,
  GeminiTestResult,
  RenderSettings,
  RetentionVaultEntry,
  SettingsResponse,
  SystemStatus,
  TrimAdjustment,
  UploadKit,
} from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== "undefined" ? "http://127.0.0.1:8000" : "");

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    let errMsg = `Request failed (${res.status})`;
    try {
      const errJson = await res.json();
      errMsg = errJson.detail || errMsg;
    } catch {
      // fallback
    }
    throw new Error(errMsg);
  }
  return res.json();
}

// ── Analysis & Cache ────────────────────────────────────────────────────────

export async function analyzeVideo(
  url: string,
  settings?: RenderSettings
): Promise<{
  success: boolean;
  cached: boolean;
  video_id: string;
  title: string;
  channel: string;
  duration_sec: number;
  thumbnail_url: string;
  download_path: string;
  audio_path: string;
  clips: ClipCandidate[];
  manual_prompt?: string | null;
}> {
  return request("/api/analyze", {
    method: "POST",
    body: JSON.stringify({ url, settings }),
  });
}

export async function parseManualGemini(
  videoId: string,
  jsonText: string
): Promise<{
  success: boolean;
  video_id: string;
  clips: ClipCandidate[];
  analysis_summary: string;
  video_type: string;
}> {
  return request(`/api/manual-gemini/parse?video_id=${encodeURIComponent(videoId)}`, {
    method: "POST",
    body: JSON.stringify({ json_text: jsonText }),
  });
}

export async function listCache(): Promise<{ success: boolean; count: number; videos: CachedVideo[] }> {
  return request("/api/cache");
}

export async function getCachedVideo(videoId: string): Promise<{
  success: boolean;
  video: Record<string, any>;
  clips: ClipCandidate[];
}> {
  return request(`/api/cache/${encodeURIComponent(videoId)}`);
}

export async function deleteCachedVideo(videoId: string): Promise<{ success: boolean; message: string }> {
  return request(`/api/cache/${encodeURIComponent(videoId)}`, { method: "DELETE" });
}

// ── Render ──────────────────────────────────────────────────────────────────

export async function renderClip(
  videoId: string,
  clipId: string,
  settings?: RenderSettings,
  trim?: TrimAdjustment,
  customCrop?: CropOverride
): Promise<{
  success: boolean;
  clip_id: string;
  status: string;
  variant_a_path: string;
  variant_b_path?: string | null;
  cover_image_path: string;
  duration_sec: number;
  encoder_used: string;
}> {
  return request("/api/render/clip", {
    method: "POST",
    body: JSON.stringify({
      video_id: videoId,
      clip_id: clipId,
      settings,
      trim,
      custom_crop: customCrop,
    }),
  });
}

export async function renderBatch(
  videoId: string,
  clipIds: string[],
  settings?: RenderSettings
): Promise<{
  success: boolean;
  rendered_count: number;
  results: any[];
  errors: any[];
}> {
  return request("/api/render/batch", {
    method: "POST",
    body: JSON.stringify({ video_id: videoId, clip_ids: clipIds, settings }),
  });
}

// ── Retention Vault ─────────────────────────────────────────────────────────

export async function listVaultEntries(): Promise<{ success: boolean; count: number; entries: RetentionVaultEntry[] }> {
  return request("/api/retention-vault");
}

export async function getVaultWinners(): Promise<{ success: boolean; count: number; winners: any[] }> {
  return request("/api/retention-vault/winners");
}

export async function logVaultEntry(entry: RetentionVaultEntry): Promise<{ success: boolean; id: number }> {
  return request("/api/retention-vault", {
    method: "POST",
    body: JSON.stringify(entry),
  });
}

export async function deleteVaultEntry(entryId: number): Promise<{ success: boolean; message: string }> {
  return request(`/api/retention-vault/${entryId}`, { method: "DELETE" });
}

// ── Batch Queue ─────────────────────────────────────────────────────────────

export async function listBatchJobs(): Promise<{ success: boolean; count: number; jobs: BatchJob[] }> {
  return request("/api/batch");
}

export async function enqueueBatch(
  urls: string[],
  settings?: RenderSettings
): Promise<{
  success: boolean;
  enqueued_count: number;
  job_ids: number[];
  message: string;
}> {
  return request("/api/batch", {
    method: "POST",
    body: JSON.stringify({ urls, settings }),
  });
}

export async function deleteBatchJob(jobId: number): Promise<{ success: boolean; message: string }> {
  return request(`/api/batch/${jobId}`, { method: "DELETE" });
}

// ── System & Explorer ───────────────────────────────────────────────────────

export async function getSystemStatus(): Promise<SystemStatus> {
  return request("/api/status");
}

export async function getSettings(): Promise<SettingsResponse> {
  return request("/api/settings");
}

export async function updateSettings(settings: Partial<SettingsResponse> & { gemini_api_key?: string }): Promise<{ success: boolean; message: string }> {
  return request("/api/settings", {
    method: "POST",
    body: JSON.stringify(settings),
  });
}

export async function testGemini(): Promise<GeminiTestResult> {
  return request("/api/gemini/test");
}

export async function openOutputFolder(videoId?: string, clipId?: string): Promise<{ success: boolean; path: string }> {
  return request("/api/open-output-folder", {
    method: "POST",
    body: JSON.stringify({ video_id: videoId, clip_id: clipId }),
  });
}

export async function getUploadKit(clipId: string): Promise<{
  success: boolean;
  clip_id: string;
  title_hook: string;
  upload_kit: UploadKit;
  cover_path: string;
  output_path_a: string;
  output_path_b?: string;
}> {
  return request(`/api/upload-kit/${encodeURIComponent(clipId)}`);
}

export async function updateUploadKit(clipId: string, kit: UploadKit): Promise<{ success: boolean; message: string }> {
  return request(`/api/upload-kit/${encodeURIComponent(clipId)}`, {
    method: "PATCH",
    body: JSON.stringify(kit),
  });
}
