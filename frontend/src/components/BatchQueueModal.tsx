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
      <div className="bg-[#121218] border border-[#262636] rounded-xl max-w-2xl w-full max-h-[85vh] flex flex-col p-5 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-[#262636]">
          <div>
            <h3 className="font-bold text-white text-sm tracking-tight flex items-center gap-2">
              <ListVideo className="w-4 h-4 text-[#FF2E93]" />
              <span>BATCH WATCHLIST QUEUE</span>
            </h3>
            <p className="text-xs text-[#7E7E9A]">Sequential unattended overnight processing</p>
          </div>
          <button
            onClick={onClose}
            className="text-[#7E7E9A] hover:text-white text-xs font-mono"
          >
            CLOSE [ESC]
          </button>
        </div>

        {/* Content */}
        <div className="py-4 space-y-4 overflow-y-auto flex-1">
          {/* Add URLs Area */}
          <div className="space-y-2">
            <label className="text-xs font-mono text-[#00F0FF]">
              PASTE YOUTUBE URLS (1 PER LINE):
            </label>
            <textarea
              value={urlsText}
              onChange={(e) => setUrlsText(e.target.value)}
              placeholder="https://www.youtube.com/watch?v=...\nhttps://youtu.be/..."
              rows={3}
              className="w-full bg-[#0A0A0F] border border-[#262636] focus:border-[#FF2E93] rounded-lg p-2.5 text-xs font-mono text-white placeholder-[#505068] outline-none"
            />
            <div className="flex justify-end">
              <button
                onClick={handleEnqueue}
                disabled={isSubmitting || !urlsText.trim()}
                className="px-4 py-1.5 bg-[#FF2E93] hover:bg-[#E02680] text-black font-bold font-mono text-xs rounded-lg disabled:opacity-40 flex items-center gap-1.5 transition-all"
              >
                {isSubmitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Plus className="w-3.5 h-3.5" />}
                <span>ADD TO BATCH QUEUE</span>
              </button>
            </div>
          </div>

          {/* Queue List */}
          <div className="space-y-2">
            <div className="text-xs font-mono text-[#7E7E9A] flex items-center justify-between">
              <span>QUEUED JOBS ({jobs.length}):</span>
              {isLoading && <Loader2 className="w-3 h-3 animate-spin text-[#00F0FF]" />}
            </div>

            {jobs.length === 0 ? (
              <div className="p-6 text-center text-xs font-mono text-[#505068] border border-dashed border-[#262636] rounded-lg">
                Queue is empty. Paste URLs above to queue unattended overnight rendering.
              </div>
            ) : (
              <div className="space-y-2">
                {jobs.map((job) => (
                  <div
                    key={job.id}
                    className="p-3 rounded-lg bg-[#0A0A0F] border border-[#262636] flex items-center justify-between gap-3 text-xs font-mono"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-white truncate">{job.video_url}</span>
                        {job.status === "processing" && (
                          <span className="px-1.5 py-0.5 rounded bg-[#00F0FF]/15 text-[#00F0FF] text-[10px] flex items-center gap-1 shrink-0">
                            <Loader2 className="w-2.5 h-2.5 animate-spin" /> PROCESSING
                          </span>
                        )}
                        {job.status === "completed" && (
                          <span className="px-1.5 py-0.5 rounded bg-green-500/15 text-green-400 text-[10px] flex items-center gap-1 shrink-0">
                            <CheckCircle2 className="w-2.5 h-2.5" /> COMPLETED
                          </span>
                        )}
                        {job.status === "queued" && (
                          <span className="px-1.5 py-0.5 rounded bg-[#7E7E9A]/15 text-[#7E7E9A] text-[10px] flex items-center gap-1 shrink-0">
                            <Clock className="w-2.5 h-2.5" /> QUEUED
                          </span>
                        )}
                        {job.status === "failed" && (
                          <span className="px-1.5 py-0.5 rounded bg-red-500/15 text-red-400 text-[10px] flex items-center gap-1 shrink-0">
                            <AlertTriangle className="w-2.5 h-2.5" /> FAILED
                          </span>
                        )}
                      </div>

                      {/* Progress Bar for Active Job */}
                      {job.status === "processing" && (
                        <div className="space-y-1 mt-1">
                          <div className="flex justify-between text-[10px] text-[#7E7E9A]">
                            <span>{job.current_stage || "Rendering"}</span>
                            <span className="text-[#00F0FF] tabular-nums">{Math.round(job.progress_pct)}%</span>
                          </div>
                          <div className="h-1 bg-[#1A1A24] rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-[#FF2E93] to-[#00F0FF] transition-all duration-300"
                              style={{ width: `${job.progress_pct}%` }}
                            />
                          </div>
                        </div>
                      )}

                      {job.error_message && (
                        <p className="text-[10px] text-red-400 truncate mt-1">
                          Error: {job.error_message}
                        </p>
                      )}
                    </div>

                    <button
                      onClick={() => handleDelete(job.id)}
                      className="p-1.5 rounded bg-[#1A1A24] hover:bg-[#262636] text-[#7E7E9A] hover:text-red-400 transition-colors"
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
