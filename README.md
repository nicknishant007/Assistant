NuroFlow

An always-on AI assistant that turns natural language and voice commands into executable workflows across your calendar, Notion, and desktop.

NuroFlow is an AI assistant platform built around one idea:

You describe what you want. NuroFlow plans it, executes it, validates the result, and responds.

The system combines a Next.js frontend, FastAPI backend, LangGraph/LangChain orchestration, OAuth integrations, Notion MCP, voice I/O, persistent conversations, and an Electron desktop companion.

        You
         │
         │ voice / text
         ▼
   ┌───────────────┐
   │    NuroFlow   │
   │  AI Assistant │
   └───────┬───────┘
           │
           ▼
      Main Planner
           │
     ┌─────┴─────────┐
     │               │
     ▼               ▼
Calendar Planner   Notion Planner
     │               │
     ▼               ▼
Calendar Executor Notion Executor
     │               │
     └──────┬────────┘
            ▼
         Validator
            │
            ▼
         Response

The desktop vision extends the same assistant:

        Floating NuroFlow
              │
       ┌──────┼─────────┐
       │      │         │
     Voice Screenshot Recording
       │      │         │
       └──────┼─────────┘
              ▼
          NuroFlow Agent

✨ What NuroFlow Does

NuroFlow is designed as a workflow-oriented AI assistant, not just a chatbot.

Core capabilities

Natural-language task understanding

Multi-step workflow planning

Domain-specific planners

Deterministic tool execution

Workflow validation

Re-planning after execution failures

Google Calendar integration

Notion integration through Notion MCP

Voice input and voice responses

Conversation persistence

OAuth-based integrations

Explicit tool registries

LangGraph orchestration

LangSmith tracing/observability

Desktop capabilities in the final feature roadmap

Always-on-top floating assistant

Voice interaction from the overlay

System-wide screenshots

Start/stop screen recording

Local screenshot and recording storage

Desktop command routing

Windows auto-start

Electron desktop shell

🧠 Core Architecture

NuroFlow separates reasoning from execution.

                         User Request
                              │
                              ▼
                    ┌──────────────────┐
                    │   Main Planner   │
                    └────────┬─────────┘
                             │
                  ┌──────────┴──────────┐
                  │                     │
                  ▼                     ▼
        ┌──────────────────┐   ┌──────────────────┐
        │ Calendar Planner │   │  Notion Planner  │
        └────────┬─────────┘   └────────┬─────────┘
                 │                      │
                 ▼                      ▼
        ┌──────────────────┐   ┌──────────────────┐
        │ Calendar Executor│   │ Notion Executor  │
        └────────┬─────────┘   └────────┬─────────┘
                 │                      │
                 └──────────┬───────────┘
                            ▼
                    ┌───────────────┐
                    │   Validator   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Response Agent│
                    └───────────────┘

Responsibilities

Main Planner

Understand the request

Select the correct domain

Handle general conversation

Detect genuinely ambiguous commands

Domain Planner

Convert the request into a complete workflow

Decide which tools are required

Resolve prerequisites and dependencies

Domain Executor

Execute the workflow deterministically

Resolve step references

Save step results

Track step status

Validator

Verify execution

Detect failures

Check required result structure

Trigger bounded re-planning when needed

Response Agent

Produce the final user-facing response

Keep internal workflow details hidden

🔄 Workflow Lifecycle

User Request
     │
     ▼
Main Planner
     │
     ├── General conversation ───────► Response
     │
     ├── Calendar ───────────────────► Calendar Planner
     │
     └── Notion ─────────────────────► Notion Planner
                                           │
                                           ▼
                                      Workflow JSON
                                           │
                                           ▼
                                        Executor
                                           │
                                           ▼
                                      Tool Calls
                                           │
                                           ▼
                                       Validator
                                      /         \
                                  success       failure
                                     │            │
                                     ▼            ▼
                                  Response     Re-plan

The LLM produces the plan. The executor performs that plan. The validator decides whether the execution was successful.

🧩 Agent Roles

Main Planner

The Main Planner is the routing layer.

It decides whether the request belongs to:

Calendar

Notion

general conversation

clarification

It should remain thin and avoid performing domain-specific operations itself.

Calendar Planner

The Calendar Planner creates workflows for:

creating events

scheduling tasks

rescheduling

deleting events/tasks

reading calendar information

multi-step calendar workflows

The Calendar Executor performs those workflows deterministically.

Notion Planner

The Notion Planner creates workflows for:

searching pages/databases

fetching resources

querying data sources

creating pages

updating pages

comments/discussions

reading comments

Example dependency references:

{{step_1.results[0].id}}

{{step_2.data_sources[0].url}}

Executors

Executors should not reinvent the plan.

A typical executor cycle is:

Read current step
      ↓
Resolve parameters
      ↓
Find registered tool
      ↓
Execute tool
      ↓
Save result
      ↓
Update status
      ↓
Move to next step

Validator

The Validator checks:

workflow step status

existence of tool results

generic tool failures

required mutation fields

execution errors

Failures may return the workflow to planning, subject to the configured retry limit.

Response Agent

The Response Agent converts execution state into a concise user-facing answer.

It should never expose internal planner names, step IDs, or implementation details.

🗃️ State Management

NuroFlow uses a shared AgentState across the graph.

It carries information such as:

user identity

conversation identity

conversation history

current goal

selected planner

generated plan

workflow steps

plan history

current workflow step

step results

step status

context

artifacts

approval state

validation results

retry state

final response

graph routing information

The shared state is the contract between graph nodes.

🧰 Tool Registry Architecture

NuroFlow uses explicit tool registries.

A registry entry describes the tool, its purpose, inputs, prerequisites, output, and executable function.

Conceptually:

TOOLS = {
    "tool_name": {
        "function": tool_function,
        "description": "...",
        "use_when": "...",
        "prerequisite_tools": [],
        "input_parameters": {...},
        "output": "...",
        "example_output": {...},
    }
}

This gives planners a structured view of available capabilities while keeping implementation details inside tool modules.

Current domains include:

Calendar
Notion

The architecture is intended to support future domains such as:

Gmail
Slack
Desktop
Files
Browser

📝 Notion Integration

NuroFlow uses Notion MCP for Notion operations.

NuroFlow
   │
   ▼
Notion Planner
   │
   ▼
Notion Executor
   │
   ▼
Synchronous Notion Tool Layer
   │
   ▼
Async Notion Service
   │
   ▼
Notion MCP

The public functions exposed to the executor are intentionally synchronous. Internal MCP/service operations may remain asynchronous.

Notion OAuth

The intended user flow is:

Settings
   │
   ▼
Connect Notion
   │
   ▼
Notion OAuth
   │
   ▼
Callback
   │
   ▼
user_integrations
   │
   ▼
provider = "notion"

The frontend must never receive raw Notion access or refresh tokens.

Notion read tools

tool access

search

fetch

data-source query

comments retrieval

Notion mutation tools

create pages

update pages

create comments

Mutations require explicit approval.

🔐 Notion Safety

Never invent:

page IDs

database IDs

data-source URLs

database property names

Use previous tool outputs through workflow references:

{{step_1.id}}

{{step_1.results[0].id}}

{{step_2.data_sources[0].url}}

For ambiguous mutation requests:

Search
   ↓
Resolve ambiguity
   ↓
Stop before mutation if unsafe

For zero results, do not invent an ID or continue into a dependent mutation.

🎙️ Voice Architecture

NuroFlow's voice pipeline is:

Microphone
    ↓
POST /voice
    ↓
Speech-to-Text
    ↓
chat_service
    ↓
LangGraph
    ↓
Workflow Execution
    ↓
Response Generation
    ↓
Text-to-Speech
    ↓
Audio Response

The desktop overlay reuses this same pipeline.

It is a new client, not a second assistant backend.

🖥️ Always-On Desktop Companion

The final feature roadmap adds an Electron desktop companion.

The desktop system is intentionally separated from the AI brain:

Electron
   =
desktop UI + desktop capabilities

FastAPI
   =
backend + authentication + services

LangGraph
   =
reasoning + orchestration

Tools
   =
external capabilities

🫧 Floating Overlay

The desktop companion will provide a small NuroFlow bubble that can:

stay always on top

remain frameless and transparent

be dragged

remember its position

expand on click

collapse on Escape/click-away

avoid a taskbar entry

Example:

        ┌──────────────────┐
        │     NuroFlow     │
        │                  │
        │       🎙         │
        │                  │
        │   Listening...   │
        │                  │
        │   Last response  │
        └──────────────────┘

The overlay can have states such as:

IDLE
LISTENING
PROCESSING
RESPONDING
ERROR

📸 Screenshot Capability

The desktop screenshot architecture is:

Voice Command
     ↓
Planner
     ↓
Desktop Tool
     ↓
Desktop Command
     ↓
Electron
     ↓
Operating System Capture
     ↓
PNG

Screenshots are stored locally:

NuroFlow/
└── Screenshots/

Example:

screenshot_2026-09-23_18-20-13.png

The initial goal is local capture. A future vision pipeline can upload the image for analysis.

🎥 Screen Recording

NuroFlow will support:

start_screen_recording
stop_screen_recording

State machine:

IDLE
  ↓
RECORDING
  ↓
STOPPING
  ↓
SAVED
  ↓
IDLE

Recordings are stored locally:

NuroFlow/
└── Recordings/

Example:

screen_recording_2026-09-23_18-25-04.webm

Invalid operations such as stopping a recording that is not running must fail safely.

🔌 Desktop Command Layer

The backend does not directly access the user's physical screen.

Instead:

FastAPI / LangGraph
        │
        ▼
Desktop Command
        │
        ▼
Electron
        │
        ▼
Operating System

The intended command contract is simple and explicit.

Example:

{
  "request_id": "abc123",
  "action": "take_screenshot"
}

The desktop client performs the local action and returns a structured result.

This architecture also leaves room for future desktop tools such as:

open_app
focus_window
open_url
read_clipboard
take_screenshot
start_screen_recording
stop_screen_recording

🔒 Security Model

The desktop layer should use a restricted Electron security model:

contextIsolation: true

nodeIntegration: false

preload scripts

explicit contextBridge methods

allowlisted IPC actions

no arbitrary shell execution

no unrestricted Node access from the renderer

no exposure of backend secrets or OAuth tokens

visible recording state

Screen capture and recording should never be silent or hidden from the user.

🔑 Authentication & Integrations

NuroFlow's integration model is user-scoped.

Google
  └── Calendar

Notion
  └── MCP

Desktop
  └── Local Electron capabilities

Integration credentials belong to the backend and are associated with the authenticated user.

The desktop client should reuse the existing authentication architecture rather than creating a separate identity system.

🗂️ High-Level Repository Structure

The exact repository structure may evolve, but the intended organization is:

NuroFlow/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── store/
│   ├── lib/
│   └── ...
│
├── Backend/
│   ├── api/
│   ├── agent/
│   │   ├── planner_agent.py
│   │   ├── notionplanner_agent.py
│   │   ├── notionexecutor_agent.py
│   │   ├── calplanner_agent.py
│   │   ├── calexecutor_agent.py
│   │   ├── validator_agent.py
│   │   └── response_agent.py
│   │
│   ├── tools/
│   │   ├── caltool_registry.py
│   │   ├── notiontool_registry.py
│   │   ├── notion_tool.py
│   │   └── ...
│   │
│   ├── services/
│   │   ├── notion/
│   │   └── ...
│   │
│   └── ...
│
└── electron/
    ├── main.ts
    ├── windows/
    ├── preload/
    ├── ipc/
    └── ...

🚀 Development Roadmap

Phase 1 — Core Agent

Main Planner

Calendar Planner

Notion Planner

Calendar Executor

Notion Executor

Validator

Response Agent

Shared state

Tool registries

Phase 2 — Integrations

Google Calendar OAuth

Notion OAuth

Notion MCP

Persistent user integrations

Conversation persistence

Phase 3 — Voice

Speech-to-text

Voice workflow execution

Text-to-speech

Voice conversation continuity

Phase 4 — Electron Shell

Electron

Main NuroFlow window

Floating overlay

Persistent overlay position

Windows auto-start

Phase 5 — Desktop Voice

Overlay microphone

Lightweight overlay state

Existing /voice pipeline

Response playback

Phase 6 — Screenshot

Desktop screenshot tool

Secure Electron IPC

Local PNG storage

Capture status

Phase 7 — Screen Recording

Start recording

Stop recording

Recording state

Local .webm storage

Recording indicator

Phase 8 — Hardening

Error handling

OAuth reconnect/disconnect

Permission handling

Desktop command reliability

Packaging

Tests

Observability

🧪 Example Interactions

Calendar

User:
Schedule a friend party tomorrow at 3:50 PM for three hours.

NuroFlow:
Main Planner
→ Calendar Planner
→ Calendar Executor
→ Validator
→ Response

Notion

User:
Find my Companies I have applied database and tell me
what companies are currently listed.

NuroFlow:
Main Planner
→ Notion Planner
→ Search
→ Fetch
→ Query Data Source
→ Validator
→ Response

Screenshot

User:
Take a screenshot.

NuroFlow:
Main Planner
→ Desktop Tool
→ Electron
→ PNG saved locally

Recording

User:
Start recording.

NuroFlow:
→ Desktop command
→ Electron
→ Recording starts

Then:

User:
Stop recording.

NuroFlow:
→ Desktop command
→ Electron
→ WebM saved locally

🧭 Design Principles

One Assistant Brain

Electron is an interface and desktop capability layer, not another planner.

Plan → Execute → Validate

LLMs plan. Deterministic executors execute. Validators verify.

Tools Are Capabilities

Calendar, Notion, and Desktop are exposed as capabilities through registries.

Shared State

Context and execution results move through the graph using a shared state contract.

Safety Before Mutation

Resolve resources, validate prerequisites, request approval where needed, then mutate.

Modular Domains

A future domain should fit the same overall pattern:

Domain Planner
     ↓
Domain Executor
     ↓
Domain Tools
     ↓
Shared Validator

🛠️ Tech Stack

Frontend

Next.js

React

TypeScript

Tailwind CSS

shadcn/ui

Zustand

Backend

Python

FastAPI

SQLAlchemy

PostgreSQL

Redis

AI / Agent Layer

LangChain

LangGraph

LangSmith

Gemini

Structured workflow planning

Integrations

Google Calendar OAuth

Notion OAuth

Notion MCP

Desktop

Electron

Electron IPC

MediaRecorder

OS display/screen capture APIs

📌 Project Status

NuroFlow is being developed incrementally.

Established architecture

Core LangGraph orchestration

Main Planner

Calendar planning/execution

Notion planning/execution architecture

Validator

Response Agent

Conversation persistence

Google Calendar integration

Notion MCP integration

Voice pipeline

Final major feature

Always-On Desktop Companion

Electron
   +
Floating Overlay
   +
Voice
   +
Screenshot
   +
Screen Recording

This desktop feature is being added without replacing the existing assistant architecture.

🎯 Vision

NuroFlow is not intended to be just another chat window.

The goal is an assistant that is available while you work.

Instead of:

Open application
→ type
→ wait
→ perform the remaining work manually

the intended experience is:

Keep working
     ↓
Speak to NuroFlow
     ↓
NuroFlow understands the goal
     ↓
Plans the workflow
     ↓
Uses the appropriate tools
     ↓
Validates execution
     ↓
Responds

Eventually:

See the NuroFlow bubble.
Speak.
Let the workflow execute.

🤝 Contributing

When adding a capability:

Define the capability.

Implement the tool.

Register the tool.

Add planner guidance.

Add prerequisite logic.

Add validation rules if needed.

Add tests.

Preserve existing domain behavior.

Avoid one-off shortcuts that bypass the shared orchestration model.

⚠️ Current Scope

The immediate desktop target is Windows-first.

Android and iOS are outside the current implementation scope.

The core desktop release is focused on:

Floating Overlay
        +
Voice
        +
Screenshot
        +
Screen Recording

❤️ NuroFlow

Natural language in.
Verified workflows out.

Think → Plan → Execute → Validate → Respond

And soon:

Work normally.
Speak naturally.
Let NuroFlow handle the workflow.
