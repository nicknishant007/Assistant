/**
 * Shared types, mirroring the Pydantic schemas in Backend/schemas/*.py.
 * Keep this file the single place the frontend defines "what a message /
 * event / user looks like" — components and stores import from here,
 * never redeclare their own shapes.
 */

export interface User {
  id: string;
  email: string;
  name: string | null;
}

// ---- Chat -----------------------------------------------------------

export type MessageRole = "user" | "assistant" | "system";

export interface ChatMessage {
  id: string;
  conversationId: string;
  role: MessageRole;
  content: string;
  createdAt: string;
  /** Present only on assistant messages that carry a structured card. */
  card?: ApprovalCardData | ClarificationCardData | null;
  /** Set while a voice reply's audio is being generated/played. */
  audioUrl?: string | null;
}

export interface ChatRequest {
  conversation_id: string | null;
  message: string;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
}

// ---- Conversations ----------------------------------------------------

export interface Conversation {
  id: string;
  title: string;
  updatedAt: string;
}

// ---- Approval / clarification (agent workflow surfaces) --------------

export interface ApprovalCardData {
  type: "approval";
  summary: string;
  onApprove: () => void;
  onReject: () => void;
}

export interface ClarificationCardData {
  type: "clarification";
  question: string;
  options?: { label: string; value: string }[];
}

// ---- Calendar ----------------------------------------------------------

export interface CalendarEvent {
  event_id: string;
  title: string;
  start_time: string; // ISO datetime
  end_time: string; // ISO datetime
}

export interface CreateEventInput {
  title: string;
  start_time: string;
  end_time: string;
}

export interface UpdateEventInput extends Partial<CreateEventInput> {
  event_id: string;
}

// ---- Voice ---------------------------------------------------------------

export type RecordingState = "idle" | "recording" | "processing" | "error";

// ---- Profile ------------------------------------------------------------

export interface UserProfile {
  id: string;
  email: string;
  full_name: string | null;
  profile_picture: string | null;
}

export interface ProfileUpdateInput {
  full_name?: string;
  profile_picture?: string;
}

// ---- Preferences ----------------------------------------------------------
// Mirrors Backend/database/models/user_preference.py — no invented fields.

export interface UserPreferences {
  wake_time: string | null; // "HH:MM:SS"
  sleep_time: string | null;
  work_start_time: string | null;
  focus_duration: number; // minutes
}

export interface PreferencesUpdateInput {
  wake_time?: string;
  sleep_time?: string;
  work_start_time?: string;
  focus_duration?: number;
}