"use client";

import { useEffect, useState } from "react";
import { PipelineTelemetry } from "@/types";

export function useTelemetry() {
  const [telemetry, setTelemetry] = useState<PipelineTelemetry>({
    stage: "idle",
    stage_label: "System Idle",
    progress_pct: 0,
    vram_used_mb: 0,
    vram_total_mb: 6144,
    vram_pct: 0,
    log_message: "Ready to analyze video.",
  });
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    let es: EventSource | null = null;
    let retryTimeout: NodeJS.Timeout | null = null;

    function connect() {
      try {
        const sseUrl = process.env.NEXT_PUBLIC_API_URL ? `${process.env.NEXT_PUBLIC_API_URL}/api/events/stream` : "http://127.0.0.1:8000/api/events/stream";
        es = new EventSource(sseUrl);

        es.onopen = () => {
          setIsConnected(true);
        };

        es.addEventListener("pipeline_event", (e) => {
          try {
            const data = JSON.parse(e.data);
            setTelemetry((prev) => ({
              ...prev,
              ...data,
            }));
          } catch (err) {
            console.error("Failed to parse pipeline_event", err);
          }
        });

        es.addEventListener("vram_heartbeat", (e) => {
          try {
            const data = JSON.parse(e.data);
            setTelemetry((prev) => ({
              ...prev,
              vram_used_mb: data.used_mb ?? prev.vram_used_mb,
              vram_total_mb: data.total_mb ?? prev.vram_total_mb,
              vram_pct: data.utilization_pct ?? prev.vram_pct,
              stage: data.current_stage !== "idle" ? data.current_stage : prev.stage,
            }));
          } catch (err) {
            console.error("Failed to parse vram_heartbeat", err);
          }
        });

        es.onerror = () => {
          setIsConnected(false);
          if (es) {
            es.close();
          }
          retryTimeout = setTimeout(connect, 3000);
        };
      } catch (err) {
        setIsConnected(false);
        retryTimeout = setTimeout(connect, 3000);
      }
    }

    connect();

    return () => {
      if (es) es.close();
      if (retryTimeout) clearTimeout(retryTimeout);
    };
  }, []);

  return { telemetry, isConnected };
}
