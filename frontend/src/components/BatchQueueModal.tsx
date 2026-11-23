"use client";

import React, { useEffect, useState } from "react";
import { X, ListVideo, Plus, Trash2, Loader2, CheckCircle2, AlertTriangle, Clock } from "lucide-react";
import { BatchJob, RenderSettings } from "@/types";
import { deleteBatchJob, enqueueBatch, listBatchJobs } from "@/lib/api";

interface BatchQueueModalProps {
  isOpen: boolean;
  onClose: () => void;
  settings: RenderSettings;
}

export const BatchQueueModal: React.FC<BatchQueueModalProps> = ({
  isOpen,
  onClose,
  settings,
}) => {
  const [jobs, setJobs] = useState<BatchJob[]>([]);
  const [urlsText, setUrlsText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchJobs = async () => {
    setIsLoading(true);
    try {
      const res = await listBatchJobs();
      setJobs(res.jobs);
    } catch (err) {
      console.error("Failed to load batch jobs", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchJobs();
      const interval = setInterval(fetchJobs, 4000);
      return () => clearInterval(interval);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleEnqueue = async () => {
    const urls = urlsText
      .split("\n")
      .map((u) => u.trim())
      .filter((u) => u.length > 0);

    if (urls.length === 0) return;

    setIsSubmitting(true);
    try {
      await enqueueBatch(urls, settings);
      setUrlsText("");
      await fetchJobs();
    } catch (err) {
      console.error("Failed to enqueue batch", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteBatchJob(id);
      await fetchJobs();
    } catch (err) {
      console.error("Failed to delete job", err);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-studio-900 border border-studio-700/80 rounded-lg max-w-2xl w-full max-h-[85vh] flex flex-col p-5 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-studio-800">
          <div>
            <h3 className="font-medium text-studio-100 text-sm tracking-tight flex items-center gap-2">
              <ListVideo className="w-4 h-4 text-studio-400" />
              <span>Batch render queue</span>
            </h3>
            <p className="text-xs text-studio-400 mt-0.5">Sequential unattended background processing</p>
          </div>
          <button
            onClick={onClose}
            className="text-studio-400 hover:text-white text-xs font-mono"
          >
            Close [Esc]
          </button>
        </div>

        {/* Content */}
        <div className="py-4 space-y-4 overflow-y-auto flex-1">
          {/* Add URLs Area */}
          <div className="space-y-2">
            <label className="text-xs font-mono text-studio-300 font-medium">
              YouTube URLs (one per line):
            </label>
            <textarea
              value={urlsText}
              onChange={(e) => setUrlsText(e.target.value)}
              placeholder="https://www.youtube.com/watch?v=...\nhttps://youtu.be/..."
              rows={3}
              className="w-full bg-studio-950 border border-studio-800 focus:border-studio-600 rounded p-2.5 text-xs font-mono text-studio-100 placeholder-studio-600 outline-none"
            />
            <div className="flex justify-end">
              <button
                onClick={handleEnqueue}
                disabled={isSubmitting || !urlsText.trim()}
                className="px-4 py-1.5 bg-tally-amber hover:bg-amber-400 text-studio-950 font-medium font-mono text-xs rounded disabled:opacity-40 flex items-center gap-1.5 transition-colors"
              >
                {isSubmitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Plus className="w-3.5 h-3.5" />}
                <span>Add to queue</span>
              </button>
            </div>
          </div>

          {/* Queue List */}
          <div className="space-y-2">
            <div className="text-xs font-mono text-studio-400 flex items-center justify-between">
              <span>Queued jobs ({jobs.length}):</span>
              {isLoading && <Loader2 className="w-3 h-3 animate-spin text-tally-amber" />}
            </div>

            {jobs.length === 0 ? (
              <div className="p-6 text-center text-xs font-mono text-studio-500 border border-dashed border-studio-800 rounded">
                Queue is empty. Paste URLs above to queue unattended rendering.
              </div>
            ) : (
              <div className="space-y-2">
                {jobs.map((job) => (
                  <div
                    key={job.id}
                    className="p-3 rounded bg-studio-950 border border-studio-800 flex items-center justify-between gap-3 text-xs font-mono"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-studio-200 truncate">{job.video_url}</span>
                        {job.status === "processing" && (
                          <span className="px-1.5 py-0.5 rounded bg-tally-amber/10 border border-tally-amber/30 text-tally-amber text-[10px] flex items-center gap-1 shrink-0">
                            <Loader2 className="w-2.5 h-2.5 animate-spin" /> Processing
                          </span>
                        )}
                        {job.status === "completed" && (
                          <span className="px-1.5 py-0.5 rounded bg-tally-emerald/10 border border-tally-emerald/30 text-tally-emerald text-[10px] flex items-center gap-1 shrink-0">
                            <CheckCircle2 className="w-2.5 h-2.5" /> Completed
                          </span>
                        )}
                        {job.status === "queued" && (
                          <span className="px-1.5 py-0.5 rounded bg-studio-800 border border-studio-700 text-studio-400 text-[10px] flex items-center gap-1 shrink-0">
                            <Clock className="w-2.5 h-2.5" /> Queued
                          </span>
                        )}
                        {job.status === "failed" && (
                          <span className="px-1.5 py-0.5 rounded bg-tally-red/10 border border-tally-red/30 text-tally-red text-[10px] flex items-center gap-1 shrink-0">
                            <AlertTriangle className="w-2.5 h-2.5" /> Failed
                          </span>
                        )}
                      </div>

                      {/* Progress Bar for Active Job */}
                      {job.status === "processing" && (
                        <div className="space-y-1 mt-1">
                          <div className="flex justify-between text-[10px] text-studio-400">
                            <span>{job.current_stage || "Rendering"}</span>
                            <span className="text-studio-200 tabular-nums">{Math.round(job.progress_pct)}%</span>
                          </div>
                          <div className="h-1 bg-studio-900 rounded overflow-hidden">
                            <div
                              className="h-full bg-tally-amber transition-all duration-300"
                              style={{ width: `${job.progress_pct}%` }}
                            />
                          </div>
                        </div>
                      )}

                      {job.error_message && (
                        <p className="text-[10px] text-tally-red truncate mt-1">
                          Error: {job.error_message}
                        </p>
                      )}
                    </div>

                    <button
                      onClick={() => handleDelete(job.id)}
                      className="p-1.5 rounded bg-studio-900 hover:bg-studio-850 border border-studio-800 text-studio-400 hover:text-tally-red transition-colors"
                      title="Remove from queue"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
