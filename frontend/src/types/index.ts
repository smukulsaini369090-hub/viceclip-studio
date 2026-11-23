export interface ViralityScorecard {
  three_second_visual_hook: number;
  replay_loop_factor: number;
  debate_comment_bait_potential: number;
  payoff_speed: number;
}

export interface UploadKit {
  titles: string[];
  hashtags: string[];
  pinned_comment: string;
  best_cover_timestamp_sec: number;
}

export interface ClipCandidate {
  id?: number;
  video_id?: string;
  clip_id: string;
  rank?: number;
  title_hook: string;
  start_sec: number;
  end_sec: number;
  duration_sec?: number;
  virality_score?: number;
  score_visual_hook?: number;
  score_replay_loop?: number;
  score_debate_bait?: number;
  score_payoff_speed?: number;
  virality?: ViralityScorecard;
  top_banner_text_a?: string;
  top_banner_text_b?: string;
  banner_text_a?: string;
  banner_text_b?: string;
  needs_easter_egg_zoom: boolean;
  easter_egg_description: string;
  upload_kit: UploadKit;
  status?: string;
  output_path_a?: string;
  output_path_b?: string;
  cover_path?: string;
}

export interface RenderSettings {
  enable_demucs: boolean;
  enable_commentary: boolean;
  enable_easter_egg_zoom: boolean;
  enable_dead_air_cut: boolean;
  enable_dual_hook: boolean;
  caption_theme: "vice_city_neon" | "rockstar_bold" | "clean_minimal";
  manual_gemini_mode: boolean;
  commentary_voice: string;
  custom_crop?: CropOverride | null;
}

export interface CropOverride {
  clip_id: string;
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface TrimAdjustment {
  clip_id: string;
  start_sec: number;
  end_sec: number;
}

export interface HeatmapPoint {
  start_sec: number;
  end_sec: number;
  intensity: number;
}

export interface AudioSpike {
  timestamp_sec: number;
  db_level: number;
  spike_type: string;
}

export interface VisualSpike {
  timestamp_sec: number;
  velocity_score: number;
  description: string;
}

export interface CachedVideo {
  video_id: string;
  url: string;
  title: string;
  channel: string;
  duration_sec: number;
  thumbnail_url: string;
  created_at: string;
  updated_at: string;
}

export interface PipelineTelemetry {
  job_id?: number;
  video_id?: string;
  stage: string;
  stage_label: string;
  progress_pct: number;
  eta_seconds?: number;
  vram_used_mb: number;
  vram_total_mb: number;
  vram_pct: number;
  log_message?: string;
  is_complete?: boolean;
  error?: string | null;
}

export interface SystemStatus {
  ffmpeg_available: boolean;
  nvenc_available: boolean;
  cuda_available: boolean;
  cuda_device?: string | null;
  vram_total_mb: number;
  encoder: string;
  python_version: string;
  workspace_dir: string;
}

export interface GeminiTestResult {
  success: boolean;
  model_name?: string;
  available_models?: string[];
  error?: string | null;
  response_preview?: string;
}

export interface SettingsResponse {
  gemini_api_key_set: boolean;
  gemini_fast_model: string;
  gemini_deep_model: string;
  whisper_model_size: string;
  nvenc_preset: string;
  target_fps: number;
  caption_theme: string;
  output_dir: string;
}

export interface RetentionVaultEntry {
  id?: number;
  clip_id: string;
  video_id: string;
  title_hook: string;
  views_48h: number;
  avd_pct: number;
  viewed_pct: number;
  swiped_pct: number;
  hook_formula: string;
  clip_pattern: string;
  banner_text: string;
  notes?: string;
  logged_at?: string;
}

export interface BatchJob {
  id: number;
  video_url: string;
  video_id: string;
  status: "queued" | "processing" | "completed" | "failed";
  priority: number;
  settings_json: string;
  progress_pct: number;
  current_stage: string;
  error_message?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}
