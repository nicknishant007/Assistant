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
