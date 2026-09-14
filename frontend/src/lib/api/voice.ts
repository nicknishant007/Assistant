import { apiClient } from "./client";

export interface VoiceResponse {
  conversation_id: string;
  response: string;
  user_message:string;
  audio_base64: string;
}

export const voiceApi = {
  async send(
    audioBlob: Blob,
    conversationId?: string | null
  ): Promise<VoiceResponse> {
    console.log("Sending Blob:", audioBlob);
    const form = new FormData();

    form.append(
      "file",
      audioBlob,
      "recording.webm"
    );
    console.log("FORM ENTRIES:");
    for (const pair of form.entries()) {
      console.log(pair[0], pair[1]);
    }

    if (conversationId) {
      form.append(
        "conversation_id",
        conversationId
      );
    }

    const { data } = await apiClient.post(
      "/voice",
      form
    );

    return data;
  }
};