# 🚀 NuroFlow

> An intelligent AI workflow assistant that understands natural-language requests, generates structured workflows, and executes them across connected services.

---

## 1. 📌 Project Overview

NuroFlow is an AI-powered workflow assistant that allows users to interact with external services through natural language.

Instead of manually navigating different applications, users can describe what they want to accomplish, and NuroFlow determines the required actions, generates a structured workflow, executes the required tools, validates the results, and returns a natural-language response.

For example:

~~~text
"Find my job application database in Notion and open the first page."
~~~

The request is processed through a structured pipeline:

~~~text
User Request
      ↓
Main Planner
      ↓
Domain Planner
      ↓
Workflow Generation
      ↓
Domain Executor
      ↓
Validator
      ↓
Response Agent
      ↓
Final Response
~~~

NuroFlow is built around a **Planner → Executor → Validator** architecture and uses **LangGraph** to orchestrate the complete workflow.

---

## 2. ✨ Key Features

### 🧠 Natural Language Interaction

Users can communicate with NuroFlow using normal conversational language instead of manually operating individual tools or services.

Example:

~~~text
"Find my job applications database in Notion."
~~~

### 🤖 Multi-Agent Architecture

NuroFlow uses specialized agents for different responsibilities:

- Main Planner
- Calendar Planner
- Notion Planner
- Calendar Executor
- Notion Executor
- Validator
- Response Agent

Each component has a focused responsibility within the overall workflow.

### 🔀 Domain-Based Planning

The Main Planner determines which domain is required for the user's request.

Currently supported domains include:

- 📝 Notion
- 🗓️ Google Calendar

The architecture is designed so additional domains can be added using the same planner/executor pattern.

### ⚙️ Structured Workflow Generation

Instead of generating one tool call at a time, the domain planner generates a complete workflow containing the steps required to accomplish the task.

### 🔧 Deterministic Tool Execution

The executor does not use an LLM for every workflow step.

The planner decides **what needs to happen**, while the executor deterministically performs the generated operations.

### 🔗 Multi-Step Tool Chaining

A workflow can contain dependencies between steps.

For example:

~~~text
{{step_1.results[0].id}}
~~~

A later workflow step can use the result produced by an earlier step.

### 💬 Clarification Handling

When required information is missing, the planner can ask the user for clarification instead of generating an incomplete workflow.

~~~text
User Request
     ↓
Planner
     ↓
Required Information Missing
     ↓
Clarification Question
     ↓
User Response
     ↓
Workflow Generation
~~~

### ✅ Validation and Retry

After execution, the workflow is validated.

If the workflow fails, the system can route the task back through the planning stage for replanning and retry.

### 🧾 Conversation Context

NuroFlow maintains conversation history so that follow-up requests can be interpreted using previous interactions.

Example:

~~~text
User:
Find my job application page in Notion.

Assistant:
I found your job application page.

User:
Open the first one.
~~~

The context from the previous interaction can be used when processing the follow-up request.

### 🔐 Authentication and Integrations

NuroFlow uses:

- JWT-based authentication for users
- OAuth-based authentication for external service integrations

---

## 3. 🏗️ System Architecture

NuroFlow follows a modular architecture where planning, execution, validation, and response generation are handled by separate components.

~~~text
                         ┌─────────────────┐
                         │      User       │
                         └────────┬────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │    Main Planner     │
                       └──────────┬──────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  │                               │
                  ▼                               ▼
        ┌──────────────────┐             ┌──────────────────┐
        │ Calendar Planner │             │  Notion Planner  │
        └────────┬─────────┘             └────────┬─────────┘
                 │                                │
                 ▼                                ▼
        ┌──────────────────┐             ┌──────────────────┐
        │Calendar Executor │             │ Notion Executor  │
        └────────┬─────────┘             └────────┬─────────┘
                 │                                │
                 └───────────────┬────────────────┘
                                 │
                                 ▼
                       ┌─────────────────────┐
                       │      Validator      │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │   Response Agent    │
                       └──────────┬──────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │      User       │
                         └─────────────────┘
~~~

The architecture separates the system into four major stages:

~~~text
Planning
   ↓
Execution
   ↓
Validation
   ↓
Response
~~~

This separation allows LLMs to handle reasoning and planning while deterministic components handle actual workflow execution.

---

## 4. 🤖 Agent Architecture

NuroFlow uses multiple specialized agents instead of relying on a single agent for the complete task.

### 🧭 Main Planner

The Main Planner is the entry point for user requests.

Its responsibilities include:

- Understanding the user request
- Determining whether the request is a general conversation or a task
- Identifying the required domain
- Routing the request to the appropriate domain planner
- Handling requests that can be answered directly

The routing concept is:

~~~text
                     Main Planner
                          │
             ┌────────────┼────────────┐
             │            │            │
             ▼            ▼            ▼
         General       Calendar      Notion
        Conversation    Planner      Planner
~~~

---

### 🗓️ Calendar Planner

The Calendar Planner handles calendar-related requests.

Its responsibilities include:

- Understanding the calendar task
- Determining the required calendar operations
- Generating the required workflow
- Providing structured parameters for the executor

Example:

~~~text
"Create a meeting with Alice tomorrow at 4 PM."
~~~

The planner converts this request into a structured workflow that can be executed by the Calendar Executor.

---

### 📝 Notion Planner

The Notion Planner handles Notion-related requests.

Its responsibilities include:

- Understanding the Notion request
- Selecting the required tools
- Generating a complete workflow
- Connecting multiple workflow steps
- Asking for clarification when required information is missing

Example:

~~~text
Step 1 → Search Notion
Step 2 → Use the result from Step 1
Step 3 → Fetch or modify the selected page
~~~

Workflow steps can reference previous results:

~~~text
{{step_1.results[0].id}}
~~~

---

### ⚙️ Domain Executor

The Domain Executor is responsible for executing the workflow generated by the domain planner.

The executor is deterministic and does not require an LLM call for every individual step.

Its execution model is:

~~~text
Generated Workflow
       ↓
Read Current Step
       ↓
Resolve Parameters
       ↓
Execute Tool
       ↓
Store Result
       ↓
Move to Next Step
~~~

This separation reduces unnecessary LLM calls and keeps execution predictable.

---

### ✅ Validator

The Validator checks the result of workflow execution.

~~~text
Executor
   ↓
Validator
   ├── Success → Response
   └── Failure → Replanning / Retry
~~~

The validator acts as a control layer between execution and the final response.

---

### 💬 Response Agent

The Response Agent receives the final workflow results and generates the user-facing response.

Example:

~~~text
Workflow Result
      ↓
Response Agent
      ↓
"Your meeting with Alice has been created for tomorrow at 4 PM."
~~~

Its purpose is to convert structured execution results into a clear conversational response.

---

## 5. 🔄 LangGraph Workflow

NuroFlow uses **LangGraph** to orchestrate the different agents and execution stages.

The graph begins with the Main Planner:

~~~text
START
  ↓
Planner
~~~

The Main Planner then routes the request depending on its type.

### General Conversation

~~~text
START
  ↓
Planner
  ↓
Response
  ↓
END
~~~

### Calendar Task

~~~text
START
  ↓
Planner
  ↓
Calendar Planner
  ↓
Calendar Executor
  ↓
Validator
  ↓
Response
  ↓
END
~~~

### Notion Task

~~~text
START
  ↓
Planner
  ↓
Notion Planner
  ↓
Notion Executor
  ↓
Validator
  ↓
Response
  ↓
END
~~~

### Failed Workflow

When validation identifies a failure, the graph can return to the planning stage:

~~~text
Executor
   ↓
Validator
   ↓
Failure
   ↓
Planner
   ↓
Replanning
   ↓
Executor
~~~

This allows the system to attempt replanning rather than immediately returning a failed result.

---

## 6. 🧠 How the Agent Works

NuroFlow follows a simple design principle:

> **LLMs decide what should happen, while deterministic components execute what was decided.**

A typical task goes through the following stages.

### Step 1 — Understand the Request

The user sends a natural-language request.

~~~text
"Find my job application database in Notion and open the first matching page."
~~~

### Step 2 — Select the Domain

The Main Planner identifies that the request belongs to the Notion domain.

~~~text
User Request
     ↓
Main Planner
     ↓
Notion Planner
~~~

### Step 3 — Generate a Complete Workflow

The Notion Planner generates the workflow required to complete the request.

Conceptually:

~~~text
Step 1 → Search Notion
Step 2 → Select the required result
Step 3 → Fetch the selected page
~~~

The generated workflow can contain dependencies between steps:

~~~text
{{step_1.results[0].id}}
~~~

### Step 4 — Execute the Workflow

The Domain Executor reads the generated workflow and executes each step sequentially.

~~~text
Workflow
   ↓
Step 1
   ↓
Store Result
   ↓
Step 2
   ↓
Store Result
   ↓
Step 3
~~~

### Step 5 — Validate the Result

After execution, the Validator checks whether the workflow completed successfully.

~~~text
Execution Result
      ↓
Validator
~~~

A successful workflow continues to the Response Agent.

A failed workflow can be routed back for replanning.

### Step 6 — Generate the Final Response

The Response Agent converts the structured result into a natural-language response.

~~~text
Validated Workflow Result
          ↓
    Response Agent
          ↓
     Final Response
~~~

The overall process can be summarized as:

~~~text
User Request
     ↓
Understand Intent
     ↓
Select Domain
     ↓
Generate Workflow
     ↓
Resolve Dependencies
     ↓
Execute Tools
     ↓
Validate Result
     ↓
Generate Response
~~~

---

## 7. 🔗 Workflow Structure

NuroFlow represents a task as a structured workflow containing individual executable steps.

A simplified workflow looks like:

~~~json
{
  "workflow": [
    {
      "id": "step_1",
      "tool": "notion-search",
      "params": {
        "query": "Companies I have applied"
      }
    },
    {
      "id": "step_2",
      "tool": "notion-fetch",
      "params": {
        "page_id": "{{step_1.results[0].id}}"
      }
    }
  ]
}
~~~

Each workflow step contains three core fields:

| Field | Description |
|-------|-------------|
| `id` | Unique identifier for the workflow step |
| `tool` | Tool that should be executed |
| `params` | Parameters required by the tool |

### 🔗 Step Dependencies

Workflow steps can reference results generated by previous steps.

For example:

~~~text
{{step_1.results[0].id}}
~~~

represents a dependency where `step_2` uses the `id` returned by `step_1`.

Conceptually:

~~~text
step_1
  ↓
results
  ↓
[0]
  ↓
id
  ↓
step_2 parameter
~~~

This allows NuroFlow to construct multi-step workflows where the output of one operation becomes the input of another.

The executor resolves these references before executing the corresponding tool.

### 📋 Workflow Execution Model

The workflow is executed sequentially:

~~~text
Workflow
   ↓
Step 1
   ↓
Result
   ↓
Step 2
   ↓
Result
   ↓
Step 3
   ↓
Final Result
~~~

This provides a structured mechanism for chaining multiple tool operations together while keeping execution deterministic.
## 8. 🛠️ Tool Registry Architecture

NuroFlow uses a registry-based tool architecture to keep tool definitions separate from the agents that execute them.

Instead of hard-coding tool information inside the planners, tools are registered with metadata describing how and when they should be used.

A tool definition can contain:

- Tool name
- Executable function
- Tool description
- When the tool should be used
- Required prerequisite tools
- Input parameters
- Expected output
- Example output

The architecture can be represented as:

    Tool Registry
          │
          ├── Tool Name
          ├── Description
          ├── Input Parameters
          ├── Prerequisites
          ├── Expected Output
          └── Executable Function

The planner uses the registered tool descriptions when generating workflows.

The executor then looks up the generated tool name in the registry and executes the corresponding function.

    Planner
       ↓
    Generated Tool Name
       ↓
    Tool Registry
       ↓
    Executable Function
       ↓
    Tool Result

This makes the architecture modular and allows new tools to be added without changing the overall agent design.

---

## 9. 📝 Notion Integration

NuroFlow integrates with Notion to allow users to interact with their Notion workspace through natural-language requests.

The Notion integration uses the Notion MCP server to communicate with Notion.

### 🔐 Notion Authentication

NuroFlow uses OAuth to connect a user's Notion workspace.

The high-level flow is:

    User
      ↓
    NuroFlow Notion Login
      ↓
    Notion Authorization
      ↓
    OAuth Callback
      ↓
    Access Token
      ↓
    Connected Notion Workspace

Once the integration is connected, the authenticated Notion account can be used by the Notion Executor while executing workflows.

### 🔧 Notion Tools

The current Notion toolset includes:

    notion-get-tool-access
    notion-search
    notion-fetch
    notion-create-pages
    notion-update-page
    notion-query-data-sources
    notion-create-comment
    notion-get-comments

These tools provide the operations required to build Notion workflows.

For example:

    User Request
         ↓
    Notion Planner
         ↓
    notion-search
         ↓
    Search Result
         ↓
    notion-fetch
         ↓
    Page Result

### 🔗 Multi-Step Notion Workflow

A Notion workflow can use the output of one tool as the input of another tool.

For example:

    Step 1
    notion-search
         ↓
    Search Result
         ↓
    {{step_1.results[0].id}}
         ↓
    Step 2
    notion-fetch

This allows NuroFlow to perform multiple dependent Notion operations as part of a single user request.

---

## 10. 🗓️ Google Calendar Integration

NuroFlow integrates with Google Calendar to allow users to manage calendar-related tasks through natural language.

Users can describe a calendar operation without manually interacting with the calendar interface.

Example:

    "Create a meeting with Alice tomorrow at 4 PM."

The request is processed through the calendar workflow:

    User Request
         ↓
    Main Planner
         ↓
    Calendar Planner
         ↓
    Calendar Workflow
         ↓
    Calendar Executor
         ↓
    Validator
         ↓
    Response Agent

### 🔐 Google OAuth

Google Calendar access is established using OAuth.

The high-level authentication flow is:

    User
      ↓
    Google Authorization
      ↓
    OAuth Callback
      ↓
    Access Token
      ↓
    Connected Calendar

The authenticated credentials are then used by the Calendar Executor when performing calendar operations.

### 📅 Calendar Workflow

A calendar request can require multiple dependent operations.

For example:

    Find Event
        ↓
    Identify Target Event
        ↓
    Use Event Information
        ↓
    Update / Delete / Reschedule

The Calendar Planner determines the required workflow, while the Calendar Executor performs the actual operations.

---

## 11. 🔐 Authentication

NuroFlow uses different authentication mechanisms for the application itself and for external service integrations.

### 👤 JWT Authentication

JWT is used to authenticate users within NuroFlow.

The general flow is:

    User Login
        ↓
    Authentication
        ↓
    JWT Generated
        ↓
    Client
        ↓
    Protected API Request
        ↓
    JWT Verification

The JWT contains the information required to identify the authenticated user.

Protected endpoints can then use the authenticated user identity when accessing application data and integrations.

### 🔗 OAuth Authentication

OAuth is used when NuroFlow needs authorized access to an external service on behalf of the user.

Currently, OAuth is used for:

    NuroFlow
       ├── Google Calendar → OAuth
       └── Notion          → OAuth

OAuth allows the application to obtain authorized access to the external service without requiring the user's external-service password.

### 🔄 Authentication Model

The two mechanisms serve different purposes:

    JWT
     ↓
    Authenticate the user with NuroFlow

    OAuth
     ↓
    Authorize NuroFlow to access external services

This separates application authentication from third-party service authorization.

---

## 12. 💬 Conversation History & Context

NuroFlow maintains conversation history so that follow-up requests can be understood using previous interactions.

Instead of treating every message as an isolated request, the planners receive conversation context when processing a new request.

### 🧠 Context-Aware Interaction

Example:

    User:
    Find my job application database in Notion.

    Assistant:
    I found your job application database.

    User:
    Open the first page.

The second request can use the context established by the earlier interaction.

The flow can be represented as:

    Conversation History
            ↓
       Main Planner
            ↓
       Domain Planner
            ↓
      Context-Aware Workflow

### 📚 Planner Context

The planning stage can use information such as:

- Previous conversation messages
- Previous planning information
- User feedback
- Existing execution context
- Validation results

This allows follow-up requests to be interpreted using information from the current conversation.

### 🔄 Conversation Flow

    User Message
         ↓
    Current Agent State
         +
    Conversation History
         ↓
    Planner
         ↓
    Updated Agent State
         ↓
    Next Interaction

Conversation history therefore becomes an important part of the agent's working context.

---

## 13. ❓ Clarification Flow

NuroFlow does not always generate a workflow immediately.

When the planner determines that required information is missing, it can ask the user for clarification before generating the workflow.

This helps avoid incomplete workflows caused by missing information.

### 🔄 Clarification Process

    User Request
          ↓
    Main Planner
          ↓
    Domain Planner
          ↓
    Required Information Missing
          ↓
    pending_question
          ↓
    Ask User
          ↓
    User Provides Information
          ↓
    Planner Runs Again
          ↓
    Complete Workflow
          ↓
    Executor

### 💬 Example

    User:
    Create a Notion page for my application.

    Assistant:
    Which Notion page or database should I add it to?

    User:
    Add it to my Companies I have applied database.

The planner can then use the user's answer together with the previous conversation context to generate the required workflow.

### 📌 Clarification State

When clarification is required, the planner can return a state containing a pending question instead of a workflow.

Conceptually:

    workflow = []

    pending_question = "Required information..."

The graph then ends the current execution and waits for the user's next message.

---

## 14. ✅ Validation & Retry Mechanism

NuroFlow contains a validation layer between workflow execution and the final response.

The purpose of validation is to determine whether the generated workflow completed successfully.

### 🔄 Validation Flow

    Workflow
        ↓
    Executor
        ↓
    Execution Result
        ↓
    Validator
       ├── Success → Response
       │
       └── Failure → Replanning

### 🧪 Validation

After workflow execution, the Validator checks the execution state and determines whether the workflow succeeded or failed.

The validation process can use information such as:

- Workflow execution status
- Step results
- Step failures
- Execution errors
- Validation results

### 🔁 Retry / Replanning

When execution fails, the workflow can be routed back to the planning stage.

    Executor
       ↓
    Validator
       ↓
    Failure
       ↓
    Planner
       ↓
    Replan
       ↓
    Executor

Instead of blindly repeating the same failed execution, the planner can generate a revised workflow.

### 📊 Retry Control

NuroFlow maintains retry information in the agent state:

    retry_count
    max_retries

This provides a limit on how many times a failed workflow can be replanned and retried.

### 🔄 Complete Control Loop

    Plan
      ↓
    Execute
      ↓
    Validate
      ↓
       ├── Success → Respond
       │
       └── Failure → Replan
                        ↓
                      Execute
                        ↓
                      Validate

The validation layer provides a reliability boundary between LLM-generated workflows and actual tool execution.
## 15. 📁 Project Structure

NuroFlow follows a modular project structure where agents, tools, services, API routes, prompts, and application state are separated based on their responsibilities.

A simplified structure of the project is:

    NuroFlow/
    │
    ├── agent/
    │   ├── state.py
    │   ├── planner_agent.py
    │   ├── calplanner_agent.py
    │   ├── notionplanner_agent.py
    │   ├── calexecutor_agent.py
    │   ├── notionexecutor_agent.py
    │   ├── validator_agent.py
    │   ├── response_agent.py
    │   ├── call_llm.py
    │   │
    │   ├── prompt/
    │   │   ├── planner_prompt.py
    │   │   ├── notionplanner_prompt.py
    │   │   └── ...
    │   │
    │   └── utils/
    │       └── messages.py
    │
    ├── tools/
    │   ├── notion_tool.py
    │   ├── notiontool_registry.py
    │   ├── calendar_tool.py
    │   ├── calendartool_registry.py
    │   └── ...
    │
    ├── services/
    │   ├── notion/
    │   │   ├── mcp_client.py
    │   │   └── ...
    │   │
    │   ├── calendar/
    │   │   └── ...
    │   │
    │   └── ...
    │
    ├── api/
    │   ├── main.py
    │   │
    │   └── routes/
    │       ├── auth.py
    │       ├── notion.py
    │       ├── calendar.py
    │       └── ...
    │
    ├── models/
    │   └── ...
    │
    ├── schemas/
    │   └── ...
    │
    ├── requirements.txt
    ├── .env
    ├── .env.example
    └── README.md

### 🧩 Main Components

| Directory | Responsibility |
|-----------|----------------|
| `agent/` | Agent logic, state management, prompts, and LangGraph workflow |
| `tools/` | Executable tools and tool registries |
| `services/` | External service and integration logic |
| `api/` | FastAPI application and API routes |
| `models/` | Database models |
| `schemas/` | Request and response schemas |

The separation keeps the codebase modular and makes it easier to extend NuroFlow with new agents, domains, or integrations.

---

## 16. 🧰 Tech Stack

NuroFlow is built using a combination of backend, agent orchestration, database, authentication, and integration technologies.

### 🐍 Backend

- **Python**
- **FastAPI**
- **Uvicorn**
- **SQLAlchemy**
- **PostgreSQL**

### 🤖 AI & Agent Framework

- **LangChain**
- **LangGraph**
- **Google Gemini**
- **LangSmith**

LangGraph is used for agent orchestration, while LangChain is used for LLM and tool-related components.

LangSmith is used for tracing and observing agent execution.

### 🔌 Integrations

- **Google Calendar**
- **Notion**
- **Notion MCP**

### 🔐 Authentication

- **JWT**
- **OAuth 2.0**
- **PKCE** for the Notion OAuth flow

### ⚡ Supporting Infrastructure

- **Redis**
- **PostgreSQL**
- **Render** for backend deployment
- **Vercel** for frontend deployment

### 🧱 Architecture Stack

The major components work together as:

    Frontend
       ↓
    FastAPI Backend
       ↓
    LangGraph
       ↓
    LangChain / LLM
       ↓
    Domain Planner
       ↓
    Domain Executor
       ↓
    Tools / Integrations
       ↓
    External Services

---

## 17. 🔑 Environment Variables

NuroFlow uses environment variables for credentials, database configuration, authentication settings, and external service integrations.

Create a `.env` file in the project root and configure the required variables.

Example:

    # Database
    DATABASE_URL=

    # JWT
    JWT_SECRET_KEY=
    ACCESS_TOKEN_EXPIRE_MINUTES=

    # Google OAuth
    GOOGLE_CLIENT_ID=
    GOOGLE_CLIENT_SECRET=
    GOOGLE_REDIRECT_URI=

    # Notion OAuth
    NOTION_CLIENT_ID=
    NOTION_CLIENT_SECRET=
    NOTION_REDIRECT_URI=

    # LLM
    GEMINI_API_KEY=

    # Redis
    REDIS_URL=

### 🔒 Security

Sensitive credentials should never be committed to the repository.

Add the following to `.gitignore`:

    .env

Use `.env.example` to document the required variables without exposing real credentials.

Example:

    DATABASE_URL=your_database_url
    JWT_SECRET_KEY=your_jwt_secret
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    GOOGLE_REDIRECT_URI=your_google_redirect_uri
    NOTION_CLIENT_ID=your_notion_client_id
    NOTION_CLIENT_SECRET=your_notion_client_secret
    NOTION_REDIRECT_URI=your_notion_redirect_uri
    GEMINI_API_KEY=your_gemini_api_key
    REDIS_URL=your_redis_url

---

## 18. 🚀 Installation & Setup

### 1. Clone the Repository

    git clone <repository-url>
    cd NuroFlow

### 2. Create a Virtual Environment

    python -m venv venv

Activate the environment.

#### Windows

    venv\Scripts\activate

#### Linux / macOS

    source venv/bin/activate

### 3. Install Dependencies

    pip install -r requirements.txt

### 4. Configure Environment Variables

Create the environment file:

    .env

Add the required credentials and configuration values.

### 5. Configure External Integrations

Set up the required OAuth applications for:

- Google
- Notion

Configure the corresponding redirect URIs in the respective developer consoles.

### 6. Configure Database

Provide the PostgreSQL connection string through:

    DATABASE_URL

Make sure the database is available before starting the application.

### 7. Configure Redis

Provide the Redis connection through:

    REDIS_URL

Redis can be used by application components that require fast temporary state or caching.

---

## 19. ▶️ Running the Project

After completing the setup, start the FastAPI backend using:

    uvicorn api.main:app --reload

The local backend will be available at:

    http://localhost:8000

FastAPI also provides interactive API documentation at:

    http://localhost:8000/docs

and:

    http://localhost:8000/redoc

### 🌐 Frontend

The frontend can be started separately using the project's frontend commands.

Typically:

    npm install
    npm run dev

The frontend then communicates with the deployed or local FastAPI backend through the configured API URL.

### 🔄 Request Flow

Once the application is running:

    Frontend
       ↓
    FastAPI API
       ↓
    Agent State
       ↓
    LangGraph
       ↓
    Planner
       ↓
    Executor
       ↓
    External Service
       ↓
    Response

---

## 20. 🌐 API Endpoints

NuroFlow exposes FastAPI endpoints for authentication, integrations, and application operations.

The API is organized into separate route modules so each integration has its own API layer.

### 🔐 Authentication

Google authentication endpoints include:

    GET /api/auth/login/google
    GET /api/auth/callback/google

The login endpoint starts the Google OAuth flow.

The callback endpoint handles the OAuth response and establishes the authenticated NuroFlow session.

### 📝 Notion

Notion-related routes include:

    GET /api/notion/login
    GET /api/notion/callback
    GET /api/notion/connection
    GET /api/notion/disconnect
    GET /api/notion/tools
    GET /api/notion/test-tool-access
    GET /api/notion/test-search

These endpoints are used for Notion authorization, connection management, tool inspection, and integration testing.

### 🗓️ Calendar

Calendar operations are exposed through the Calendar API routes.

The exact endpoints depend on the enabled calendar functionality and can be inspected through the FastAPI documentation.

### 📚 Interactive API Documentation

When the backend is running, all registered routes can be explored through:

    http://localhost:8000/docs

The Swagger interface allows requests to be tested directly against the backend.

---

## 21. 💡 Example User Queries

NuroFlow is designed to accept natural-language requests instead of requiring users to understand the underlying tools.

### 📝 Notion Examples

    "Find my Companies I have applied database in Notion."

    "Open the first page from my job applications."

    "Create a page in my applications database."

    "Update the status of this application."

    "Add a comment to this Notion page."

### 🗓️ Google Calendar Examples

    "Create a meeting with Alice tomorrow at 4 PM."

    "Find my meeting with John."

    "Reschedule my meeting with John to tomorrow at 5 PM."

    "Delete my meeting with Alice."

### 💬 Context-Aware Follow-Up

NuroFlow can also process follow-up requests using the existing conversation context.

Example:

    User:
    Find my job application database in Notion.

    Assistant:
    I found your job application database.

    User:
    Open the first page.

The second request can use the context from the previous interaction to determine what the user is referring to.

### 🔄 Multi-Step Request

A user can also describe a task that requires multiple operations:

    "Find my job application database in Notion and open the first matching page."

Conceptually, the system can execute:

    Search Notion
         ↓
    Select Matching Result
         ↓
    Extract Page ID
         ↓
    Fetch Page
         ↓
    Validate Result
         ↓
    Respond

The user only needs to describe the desired outcome; NuroFlow handles the workflow generation and execution internally.

## 22. 🚀 Example Usage

NuroFlow is designed to let users describe tasks naturally without needing to know the underlying tools or APIs.

### 📝 Notion

Example:

    "Find my Companies I have applied database in Notion."

The system can process this request as:

    User Request
         ↓
    Main Planner
         ↓
    Notion Planner
         ↓
    Search Workflow
         ↓
    Notion Executor
         ↓
    Validator
         ↓
    Response

Another example:

    "Find my job application database and open the first page."

This can result in a multi-step workflow:

    Step 1 → Search for the database
    Step 2 → Select the required result
    Step 3 → Fetch the selected page
    Step 4 → Validate the result
    Step 5 → Respond

### 🗓️ Google Calendar

Example:

    "Create a meeting with Alice tomorrow at 4 PM."

The task follows the calendar execution pipeline:

    User Request
         ↓
    Main Planner
         ↓
    Calendar Planner
         ↓
    Calendar Executor
         ↓
    Validator
         ↓
    Response

### 💬 Follow-Up Requests

NuroFlow can use conversation context for follow-up requests.

Example:

    User:
    Find my job applications database in Notion.

    Assistant:
    I found your job applications database.

    User:
    Open the first page.

The second request can be interpreted using information from the previous conversation.

---

## 23. ☁️ Deployment Architecture

NuroFlow can be deployed as separate frontend and backend applications.

The current deployment architecture is:

    ┌─────────────────────┐
    │      Frontend       │
    │       Vercel        │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │      FastAPI        │
    │       Backend       │
    │       Render        │
    └──────────┬──────────┘
               │
       ┌───────┼────────┐
       │       │        │
       ▼       ▼        ▼
    PostgreSQL Redis  External
                     Integrations
                     ├── Notion
                     └── Google
                         Calendar

### 🌐 Frontend

The frontend is deployed using **Vercel**.

It communicates with the FastAPI backend using the configured backend API URL.

### ⚙️ Backend

The FastAPI backend is deployed using **Render**.

The backend is responsible for:

- API requests
- Authentication
- Agent execution
- LangGraph orchestration
- Tool execution
- Integration handling

### 🗄️ Database

PostgreSQL is used for persistent application data.

### ⚡ Redis

Redis is used where fast temporary data or application state is required.

### 🔐 Production OAuth

OAuth redirect URLs must use the deployed backend URL rather than local development URLs.

For example:

    Local:
    http://localhost:8000/...

    Production:
    https://<deployed-backend>/...

The corresponding production redirect URI must also be configured in the external provider's developer console.

---

## 24. 🧠 Design Decisions

NuroFlow is designed around separating **reasoning, planning, execution, and validation**.

### Why LangGraph?

LangGraph provides a stateful graph-based execution model for coordinating multiple agents and controlling transitions between planning, execution, validation, and response stages.

Instead of manually managing complex agent transitions, the system represents them as graph nodes and conditional routes.

### Why Multiple Agents?

Different stages of the system have different responsibilities.

    Main Planner
        ↓
    Domain Planner
        ↓
    Executor
        ↓
    Validator
        ↓
    Response Agent

This keeps each component focused on a specific task rather than placing the complete responsibility inside a single agent.

### Why Domain Planners?

Different external services have different tools, data structures, and workflows.

Instead of giving every tool to a single planner, NuroFlow uses domain-specific planners.

For example:

    User Request
         ↓
    Main Planner
         ├── Calendar Planner
         └── Notion Planner

This allows each domain to have its own workflow-generation logic.

### Why Deterministic Executors?

The planner generates the workflow, but the executor performs the actual tool calls deterministically.

This gives the architecture a clear separation:

    LLM
     ↓
    Decide What To Do
     ↓
    Structured Workflow
     ↓
    Deterministic Code
     ↓
    Execute

This also avoids unnecessary LLM calls during every workflow step.

### Why a Tool Registry?

The tool registry provides a common interface for defining tools and their metadata.

This makes tools easier to:

- Discover
- Describe
- Validate
- Execute
- Extend

Adding another tool does not require redesigning the entire agent architecture.

### Why Validation?

LLM-generated workflows and external tool execution can fail for different reasons.

The Validator provides an additional layer between execution and the final response.

    Execute
       ↓
    Validate
       ↓
    Success / Replan

### Why Conversation Context?

Many assistant interactions are naturally multi-turn.

Maintaining conversation context allows the system to understand references and follow-up requests without requiring the user to repeat the complete task every time.

---

## 25. ✅ Current Capabilities

The current NuroFlow implementation includes the following capabilities:

### 🤖 Agent System

- Main Planner
- Calendar Planner
- Notion Planner
- Calendar Executor
- Notion Executor
- Validator
- Response Agent
- LangGraph-based orchestration

### 🔗 Workflow System

- Structured workflow generation
- Sequential workflow execution
- Multi-step tool chaining
- Step-to-step result references
- Deterministic parameter resolution
- Validation
- Replanning and retry

### 📝 Notion

- Notion OAuth integration
- Notion MCP integration
- Notion search
- Notion page fetching
- Notion page creation
- Notion page updates
- Notion comments
- Data-source related operations

### 🗓️ Google Calendar

- Google OAuth integration
- Calendar workflow planning
- Calendar tool execution
- Event-related task handling

### 🔐 Authentication

- JWT-based application authentication
- OAuth-based third-party integrations

### 💬 Conversation

- Conversation history
- Context-aware planning
- Follow-up request handling
- Clarification questions for missing information

---

## 26. ⚠️ Limitations

Although NuroFlow supports multi-step agent workflows, several areas are still under development.

### 🧠 LLM Dependency

Planning quality depends on the selected LLM.

Incorrect or incomplete model outputs can affect workflow generation and may require validation or replanning.

### 🔄 External Service Dependency

Tool execution depends on the availability and behavior of external services such as Notion and Google Calendar.

Failures in third-party APIs can therefore affect workflow execution.

### 📝 Domain Coverage

The current system supports selected domains such as:

    Notion
    Google Calendar

Additional domains are not yet integrated into the current architecture.

### 👤 Human Approval Layer

A dedicated approval flow for sensitive mutation operations is not currently part of the active workflow.

The current system focuses on planning, execution, validation, and response.

### 🤖 Autonomous Scope

NuroFlow currently operates within the tools and workflows explicitly implemented in the system.

It is not an unrestricted autonomous agent capable of independently operating arbitrary external applications.

### 🧪 Production Hardening

Additional work may be required for areas such as:

- More extensive integration testing
- Failure recovery
- Observability
- Rate-limit handling
- Large-scale concurrent execution
- More advanced workflow validation

---

## 27. 🛣️ Future Roadmap

NuroFlow is designed so additional capabilities can be introduced without changing the complete architecture.

### 🔌 More Integrations

Potential future domains include:

    Gmail
    Google Drive
    Slack
    Tasks
    More productivity services

These can follow the existing pattern:

    Main Planner
         ↓
    Domain Planner
         ↓
    Domain Executor
         ↓
    Validator

### 🧠 Better Memory

Future versions can introduce more advanced long-term memory and retrieval mechanisms for maintaining useful information across conversations.

### ✅ Human-in-the-Loop Approval

A future approval layer can be introduced for operations where explicit user confirmation is required.

Conceptually:

    Planner
       ↓
    Approval
       ↓
    Executor
       ↓
    Validator

### ⚡ Background Execution

Long-running workflows can be moved to background execution using dedicated task or message-queue infrastructure.

### 📈 Better Observability

Future improvements can include deeper execution tracing, workflow metrics, failure analysis, and performance monitoring.

### 🧩 Expanded Agent Capabilities

The same planner/executor architecture can be extended to support more complex workflows and additional domains without replacing the core architecture.

---

## 28. 📄 License

The project license can be added here once the repository license is finalized.

Example:

    MIT License

For now, replace this section with the license selected for the project.

---

## 29. 👨‍💻 Author & Contact

### Nishant Kumar

NuroFlow is developed as an AI workflow automation project focused on combining LLM-based planning with deterministic tool exection.
For questions, suggestions, or collaboration, open an issue in the repository or use the contact information provided above.
