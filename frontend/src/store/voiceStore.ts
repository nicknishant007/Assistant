import { create } from "zustand";
import { voiceApi } from "@/lib/api/voice";
import type { RecordingState } from "@/types";

interface VoiceState {
  recordingState: RecordingState;
  mediaRecorder: MediaRecorder | null;
  chunks: Blob[];
  playbackUrl: string | null;
  error: string | null;

  startRecording: () => Promise<void>;
  stopRecording: () => Promise<Blob | null>;
  cancelRecording: () => void;
  sendRecording: (blob: Blob) => Promise<void>;
}

export const useVoiceStore = create<VoiceState>((set, get) => ({
  recordingState: "idle",
  mediaRecorder: null,
  chunks: [],
  playbackUrl: null,
  error: null,

  startRecording: async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.start();

      set({ mediaRecorder: recorder, chunks, recordingState: "recording", error: null });
    } catch {
      set({
        recordingState: "error",
        error: "Microphone permission was denied or is unavailable."
      });
    }
  },

  stopRecording: async () => {
    const { mediaRecorder, chunks } = get();
    if (!mediaRecorder) return null;

    return new Promise((resolve) => {
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: mediaRecorder.mimeType || "audio/wevm" });
        mediaRecorder.stream.getTracks().forEach((t) => t.stop());
        set({ recordingState: "processing" });
        resolve(blob);
      };
      mediaRecorder.stop();
    });
  },

  cancelRecording: () => {
    const { mediaRecorder } = get();
    mediaRecorder?.stream.getTracks().forEach((t) => t.stop());
    set({ mediaRecorder: null, chunks: [], recordingState: "idle" });
  },

  sendRecording: async (blob) => {
  set({recordingState: "processing",error: null});

  try {const response =await voiceApi.send(blob);
    const audioBlob = new Blob(
      [Uint8Array.from(atob(response.audio_base64),c => c.charCodeAt(0))],
      {type: "audio/mpeg"});
    const playbackUrl =URL.createObjectURL(audioBlob);
    set({playbackUrl,recordingState: "idle"});
  } catch (err) {
    set({recordingState: "error",
      error:
        err instanceof Error
          ? err.message
          : "Voice request failed."
    });

  }
}
}));
