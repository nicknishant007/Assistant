import { apiClient } from "./client";

/**
 * Backend/api/routes/voice.py takes multipart audio and returns an
 * audio/mpeg stream directly (not JSON) — the transcript + assistant text
 * never come back separately, so the UI has to play the returned blob and
 * infer state from the request lifecycle rather than parsing a body.
 */
export const voiceApi = {
  async send(audioBlob: Blob): Promise<Blob> {
    const form = new FormData();
    form.append("file", audioBlob, "recording.wav");

    const { data } = await apiClient.post("/voice", form, {
      headers: { "Content-Type": "multipart/form-data" },
      responseType: "blob"
    });

    return data as Blob;
  }
};
