# NuroFlow Frontend — Architecture

This document is the map. Read it before editing anything — it explains
*why* each piece exists, so future changes go in the right place instead
of growing a second copy of something that already exists.

## 1. Tech stack (as specified)

Next.js 15 (App Router) · TypeScript (strict) · Tailwind CSS · Zustand ·
Axios · React Hook Form + Zod · Sonner · Lucide React · FullCalendar ·
MediaRecorder API for voice.

## 2. Folder structure

```
nuroflow/
├─ src/
│  ├─ app/                        # routes only — no business logic
│  │  ├─ layout.tsx                # fonts, <Toaster/>, global providers
│  │  ├─ globals.css               # CSS variables (theme) + Tailwind
│  │  ├─ page.tsx                  # "/" → redirect to /chat or /login
│  │  ├─ (auth)/
│  │  │  └─ login/page.tsx
│  │  └─ (app)/                    # everything behind AuthGuard
│  │     ├─ layout.tsx              # wraps children in <AuthGuard>
│  │     ├─ chat/page.tsx           # "/chat" — new conversation
│  │     ├─ chat/[conversationId]/page.tsx
│  │     ├─ calendar/page.tsx
│  │     └─ settings/page.tsx
│  │
│  ├─ theme/                      # design tokens — see §4
│  ├─ lib/
│  │  ├─ api/                     # one file per backend resource
│  │  └─ utils/                   # cn(), date formatting
│  ├─ types/                      # shared TS types, mirrors backend schemas
│  ├─ store/                      # Zustand stores — see §5
│  └─ components/
│     ├─ ui/                      # dumb, reusable primitives (Button, Card…)
│     ├─ layout/                  # AppShell, Sidebar, ContextPanel
│     ├─ chat/                    # chat-feature components
│     ├─ calendar/                # calendar-feature components
│     ├─ voice/                   # voice recorder
│     └─ shared/                  # cross-feature (AuthGuard)
```

**Why feature folders under `components/`, not one flat folder:** a
developer working on calendar should never have to scroll past 40 chat
components to find `CalendarView.tsx`. `ui/` is the exception — those
components don't know what feature is using them.

**Why `app/` only contains route files:** page components are thin. They
compose `AppShell` + one feature component and pass down route params.
All real logic lives in `components/<feature>` and `store/`, so it's
testable without Next.js's routing context.

## 3. Route structure

| Route | Access | Purpose |
|---|---|---|
| `/` | public | Redirects based on auth state |
| `/login` | public | Google OAuth entry point |
| `/chat` | private | New conversation, empty state |
| `/chat/:conversationId` | private | Existing conversation |
| `/calendar` | private | Month/week/day calendar |
| `/settings` | private | Account + integrations |

Route groups `(auth)` and `(app)` share no layout chrome — `(app)` is the
only one wrapped in `AuthGuard`, so adding a new private page is just
"create a file under `(app)/`".

## 4. Design tokens — rebranding without touching components

Everything visual traces back to `src/theme/*.ts`:

```
theme/colors.ts       →  --color-* CSS vars in globals.css  →  Tailwind colors
theme/typography.ts   →  --font-*                            →  Tailwind fontFamily
theme/spacing.ts       (referenced directly where Tailwind's default scale isn't enough)
theme/radius.ts       →  --radius-*                          →  Tailwind borderRadius
theme/shadows.ts      →  --shadow-*                          →  Tailwind boxShadow
```

No component ever writes a hex code, a `px` shadow value, or a font name.
They only ever use Tailwind classes like `bg-mint`, `shadow-md`,
`rounded-lg`, `font-display`. **To reskin NuroFlow:** edit the six files
in `theme/`, copy the resulting values into the `:root` block in
`globals.css` (or wire a small build step to generate that block —
noted as a TODO at the top of `globals.css`), and every screen updates:
sidebar, chat, calendar, modals, drawers, approval cards, auth pages.

The current palette (cream paper, mint sidebar, cobalt primary, pink for
user messages, yellow for "needs attention" states) and the hard offset
shadows/thick borders come directly from the reference boards provided —
see `theme/shadows.ts` and `theme/colors.ts` for the reasoning behind
each token's *job*, not just its color.

## 5. State management — one store per bounded concern

| Store | Owns | Notably does NOT own |
|---|---|---|
| `authStore` | current user, session status | conversations, messages |
| `chatStore` | messages per conversation, typing state | conversation *list* metadata |
| `conversationStore` | sidebar list, search, active id | message contents |
| `calendarStore` | events, selected event, modal/drawer open state | chat state |
| `voiceStore` | MediaRecorder lifecycle, playback URL | transcript text (that becomes a chat message once the backend responds) |
| `uiStore` | sidebar drawer open, context panel collapsed, active modal id | anything feature-specific |

**Why split `chatStore` and `conversationStore`:** the sidebar (list of
conversations) re-renders on a totally different cadence than the active
conversation's messages. Combining them would mean every new token/message
re-renders the sidebar too.

Each store exposes actions that call the API layer directly and update
state optimistically where it's safe (e.g. deleting a conversation removes
it immediately, rolls back on failure). Components never call `apiClient`
or `axios` directly — only stores and the `lib/api/*` modules do.

## 6. API layer

One file per backend resource under `lib/api/`, each a thin, typed
wrapper around the shared `apiClient` (`lib/api/client.ts`). `apiClient`
centralizes:

- `baseURL` from `NEXT_PUBLIC_API_BASE_URL` (never hardcoded per-call)
- `withCredentials: true`, because auth is a cookie set by the backend
  (see `Backend/api/routes/auth.py`), not a bearer token the frontend
  manages
- a response interceptor that turns FastAPI's `{ detail: string }` error
  body into a single `ApiError` class, so UI code does `catch (err) {
  err.message }` and never touches Axios/FastAPI specifics

## 7. Data flow (example: sending a chat message)

```
ChatInput (component)
  → onSend(text)
  → chatStore.sendMessage(conversationId, text)
      → optimistic: append user ChatMessage to messagesByConversation
      → chatApi.send(text, conversationId)   [lib/api/chat.ts]
          → POST /chat  { conversation_id, message }
      → on success: append assistant ChatMessage, upsert conversationStore
      → on failure: set chatStore.error, component renders an inline Card
  → ChatWindow re-renders (subscribed to chatStore.messagesFor(id))
```

Voice follows the same shape but through `voiceStore` / `voiceApi`, and
because `Backend/api/routes/voice.py` returns raw audio (not JSON), the
frontend can only play the reply — it cannot currently show the
assistant's text alongside it (see gap list below).

## 8. Error handling strategy

| Case | Where handled | UX |
|---|---|---|
| 401 | `AuthGuard` (via `authStore.hydrate` failing) | redirect to `/login` |
| 403 / 404 | `ApiError` caught at the store action | inline `Card` with the message, action stays retryable |
| 500 / network failure | same `ApiError` path | same inline `Card`; `sonner` toast for actions that aren't inline (e.g. calendar create/delete) |
| API timeout | Axios rejects → same `ApiError` path | same as above |
| Voice upload failure | `voiceStore.sendRecording` catch | recorder shows an inline error + "Retry" |
| Audio playback failure | native `<audio>`/`Audio()` error event (attach as needed in `MessageBubble`) | falls back to showing the text only |

The rule: **stores catch and normalize, components only render state**
(`error`, `loading`, or data) — no component has its own try/catch around
an API call.

## 9. Responsive behavior

- **Sidebar:** fixed column ≥ `lg` (1024px); below that, `AppShell`
  renders it as an off-canvas drawer toggled from a mobile header.
- **Context panel:** hidden below `xl` (1280px) entirely — it's
  supplementary information, not core to completing a task on a small
  screen.
- **Calendar:** FullCalendar's own `dayGridMonth/timeGridWeek/timeGridDay`
  toolbar buttons remain available at all sizes; wire a `useMediaQuery`
  check in `CalendarView` to default to `timeGridDay`/agenda-style below
  `sm` if the month grid proves too cramped in testing.
- **Voice controls:** all interactive targets in `VoiceRecorder` are
  ≥ 40px (`IconButton` is 40×40) for touch.

## 10. Known contract gaps between this brief and the actual backend

The brief describes some endpoints that don't exist yet in the provided
`Backend/` code. The frontend is built defensively against these (typed,
isolated to one `lib/api/*` file each, fails soft where possible) so
backend work can land without a frontend rewrite:

1. **No `/conversations` endpoints.** `Backend/main.py` never registers a
   conversations router, even though `ConversationMessage`/
   `AgentConversation` models and `services/conversation_service.py`
   exist. `conversationStore.fetchAll()` catches the 404 and just shows
   whatever's been added locally as conversations are created.
2. **No register/refresh endpoints.** Auth is Google-OAuth-only
   (`/api/auth/login/google`, `/api/auth/callback/google`), there's no
   password flow. The login page reflects that instead of showing a form
   the backend can't serve.
3. **Chat responses are plain strings.** `ChatResponse` is
   `{ conversation_id, response }` — approval requests, clarification
   questions, and errors from `AgentState` all collapse into `response`
   as text (see `chat_service.py`). `ApprovalCard`/`ClarificationCard`
   are built and ready, but `chatStore` currently renders everything as
   a plain assistant message; wiring them up needs the backend to return
   a `kind`/`card` field instead of only `response`.
4. **No workflow-resume endpoint.** Once an approval card exists, the UI
   needs somewhere to send "approved"/"rejected" back to the agent
   mid-workflow. That endpoint doesn't exist yet.
5. **Calendar routes live under `/api/auth/events*`,** not `/calendar/*`
   as in the brief — `lib/api/calendar.ts` points at the real paths.
6. **Voice returns audio, not JSON.** `/voice` streams back an MP3
   directly, so the frontend can play the reply but can't currently show
   the assistant's transcript text next to it without a backend change to
   also return the text (e.g. as a response header or a JSON+base64
   payload).

None of these block the rest of the app — they're isolated to the
specific store/API file noted above.
