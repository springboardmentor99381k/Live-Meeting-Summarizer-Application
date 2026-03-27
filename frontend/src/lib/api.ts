const API_BASE = (
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL.replace(/\/$/, "")}/api` : "/api")
).replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);

  const isJson = (response.headers.get("content-type") || "").includes("application/json");
  const payload = isJson ? await response.json() : null;

  if (!response.ok) {
    const message = payload?.error || `Request failed: ${response.status}`;
    throw new Error(message);
  }

  return payload as T;
}

export interface UploadResponse {
  wav_path: string;
}

export interface PipelineResponse {
  wav_path: string;
  transcript: string;
  segments: Array<{ start: number; end: number; speaker: string }>;
  diarization_path: string;
  conversation_text: string;
  conversation_txt_path: string;
  summary: string;
  meeting_title: string;
  speaker_count: number;
  duration: string;
  merge_mode: string;
}

export interface StartRecordingResponse {
  status: string;
  transcription: string;
}

export interface StopRecordingResponse {
  status: string;
  wav_path: string;
  transcript: string;
}

export interface LiveTranscriptResponse {
  transcript: string;
}

export function startRecording() {
  return request<StartRecordingResponse>("/start-recording", { method: "POST" });
}

export function stopRecording() {
  return request<StopRecordingResponse>("/stop-recording", { method: "POST" });
}

export function getLiveTranscript() {
  return request<LiveTranscriptResponse>("/live-transcript");
}

export function uploadAudio(file: File) {
  const body = new FormData();
  body.append("file", file);

  return request<UploadResponse>("/upload", {
    method: "POST",
    body,
  });
}

export function runPipeline(input: { wavPath: string; meetingTitle?: string; attendees?: string }) {
  return request<PipelineResponse>("/run-pipeline", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      wav_path: input.wavPath,
      meeting_title: input.meetingTitle || "",
      attendees: input.attendees || "",
    }),
  });
}
