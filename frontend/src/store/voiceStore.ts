import { create } from "zustand";
import { voiceApi } from "@/lib/api/voice";
import type { RecordingState } from "@/types";
import { useChatStore } from "./chatStore";
import { useConversationStore } from "./conversationStore";

interface VoiceState {
  recordingState: RecordingState;
  mediaRecorder: MediaRecorder | null;
  chunks: Blob[];
  playbackUrl: string | null;
  error: string | null;

  startRecording: () => Promise<void>;
  stopRecording: () => Promise<Blob | null>;
  cancelRecording: () => void;

  sendRecording: (
    blob: Blob,
    conversationId?: string | null
  ) => Promise<{ conversationId: string } | void>;
}

export const useVoiceStore = create<VoiceState>((set, get) => ({
  recordingState: "idle",
  mediaRecorder: null,
  chunks: [],
  playbackUrl: null,
  error: null,

  startRecording: async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true
      });

      const recorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      recorder.ondataavailable = (e) => {
        chunks.push(e.data);
      };

      recorder.start();

      set({
        mediaRecorder: recorder,
        chunks,
        recordingState: "recording",
        error: null
      });
    } catch {
      set({
        recordingState: "error",
        error: "Microphone permission was denied or is unavailable."
      });
    }
  },

  stopRecording: async () => {
    const { mediaRecorder, chunks } = get();

    if (!mediaRecorder) {
      return null;
    }

    return new Promise((resolve) => {
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, {
          type: mediaRecorder.mimeType || "audio/webm"
        });

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

    set({
      mediaRecorder: null,
      chunks: [],
      recordingState: "idle"
    });
  },

  sendRecording: async (blob, conversationId = null) => {
    set({ recordingState: "processing", error: null });

    try {
      const response = await voiceApi.send(blob, conversationId);

      // Decode MP3 from backend FIRST so we can attach it to the assistant message
      const audioBlob = new Blob(
        [
          Uint8Array.from(atob(response.audio_base64), (c) =>
            c.charCodeAt(0)
          )
        ],
        { type: "audio/mpeg" }
      );
      const playbackUrl = URL.createObjectURL(audioBlob);

      // Add user transcript to chat
      useChatStore
        .getState()
        .appendMessage(response.conversation_id, "user", response.user_message);

      // Add assistant reply WITH the audio attached, so MessageBubble shows a play button
      useChatStore
        .getState()
        .appendMessage(
          response.conversation_id,
          "assistant",
          response.response,
          playbackUrl
        );

      useConversationStore.getState().upsertLocal({
        id: response.conversation_id,
        title: response.user_message.slice(0, 50),
        updatedAt: new Date().toISOString()
      });

      useConversationStore.getState().setActive(response.conversation_id);

      set({
        playbackUrl,
        recordingState: "idle"
      });

      // Autoplay the reply once (browsers may block this silently — the
      // message's own play button in MessageBubble is the reliable fallback)
      new Audio(playbackUrl).play().catch(() => {});

      return { conversationId: response.conversation_id };
    } catch (err) {
      set({
        recordingState: "error",
        error: err instanceof Error ? err.message : "Voice request failed."
      });
    }
  }
}));