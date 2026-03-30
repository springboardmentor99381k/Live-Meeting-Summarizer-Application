import type { PipelineResponse } from "@/lib/api";

const LAST_PIPELINE_KEY = "meetmind:lastPipeline";

export function saveLastPipeline(result: PipelineResponse): void {
  localStorage.setItem(LAST_PIPELINE_KEY, JSON.stringify(result));
}

export function getLastPipeline(): PipelineResponse | null {
  const raw = localStorage.getItem(LAST_PIPELINE_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as PipelineResponse;
  } catch {
    return null;
  }
}
