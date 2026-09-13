# NuroFlow

Frontend for the NuroFlow AI Executive Assistant. See **ARCHITECTURE.md**
for the full design doc (folder structure, state management, theming,
data flow, error handling, and a list of backend contract gaps worth
knowing about before wiring things up).

## Setup

```bash
cp .env.example .env.local     # point NEXT_PUBLIC_API_BASE_URL at your FastAPI backend
npm install
npm run dev
```

Requires the `Backend/` FastAPI service running (see its own README/
`main.py`) with `SessionMiddleware` and CORS configured to allow this
frontend's origin with credentials.

## Rebranding

All visual identity lives in `src/theme/*.ts` → `src/app/globals.css`
CSS variables → Tailwind tokens. Change the six files under `src/theme/`
and mirror the values into the `:root` block of `globals.css` — no
component needs to change. Details in ARCHITECTURE.md §4.

## What's implemented vs. scaffolded

**Implemented end-to-end:** chat (text), conversation list, calendar
(list/create/delete via FullCalendar), voice recording UI, auth
guard + Google OAuth login, responsive shell (sidebar drawer, collapsible
context panel), full design-token theme.

**Scaffolded, waiting on backend support** (see ARCHITECTURE.md §10):
approval/clarification cards render real UI but chat responses need a
structured `kind` field to trigger them; conversation history persistence
needs `/conversations` endpoints; voice replies play audio but can't show
the assistant's text yet.
