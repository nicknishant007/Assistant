from tools.tool_registry import TOOLS
from agent.state import AgentState


APPROVAL_REQUIRED_TOOLS = {
    "delete_task": "delete_event",
    "update_task": "update_event",
    "schedule_task_fixed_time": "schedule_event",
    "reschedule_task": "reschedule_event",
    "reschedule_task_next_available": "reschedule_event",
}


def executor_agent(
    state: AgentState
) -> AgentState:

    workflow = state.workflow

    # --------------------------------------------------
    # NO WORKFLOW
    # --------------------------------------------------

    if not workflow:

        state.error = "No workflow found"

        state.next_step = "response"
        state.next_agent = "response"

        return state

    # --------------------------------------------------
    # WORKFLOW ALREADY COMPLETE
    # --------------------------------------------------

    if state.current_workflow_step >= len(workflow):

        state.final_response = (
            "Workflow completed successfully."
        )

        state.next_step = "response"
        state.next_agent = "response"

        return state

    current_step = workflow[
        state.current_workflow_step
    ]

    step_id = current_step["id"]

    tool_name = current_step["tool"]

    params = current_step.get(
        "params",
        {}
    )

    tool_meta = TOOLS.get(
            tool_name
        )

    if tool_meta is None:

            state.error = (
                f"Tool not found: {tool_name}"
            )

            state.next_step = "response"

            return state

    tool = tool_meta.get(
            "function"
        )

    if tool is None:

            state.error = (
                f"No executable function for tool: {tool_name}"
            )

            state.next_step = "response"

            return state

    result = tool(
            db=state.db,
            user_id=state.user_id,
            **params
        )

    # --------------------------------------------------
    # EXECUTE TOOL
    # --------------------------------------------------

    try:

        result = tool(
            db=state.db,
            user_id=state.user_id,
            **params
        )

    except Exception as e:

        state.error = str(e)

        state.step_status[
            step_id
        ] = "failed"

        state.next_step = "response"
        state.next_agent = "response"

        return state

    # --------------------------------------------------
    # SAVE RESULT
    # --------------------------------------------------

    state.step_results[
        step_id
    ] = result

    state.step_status[
        step_id
    ] = "completed"

    # --------------------------------------------------
    # EVENT MATCH APPROVAL
    # --------------------------------------------------

    if tool_name == "find_event_by_title":

        matches = result.get(
            "matches",
            []
        )

        if len(matches) > 1:

            state.candidate_events = matches

            state.approval_required = True

            state.approval["pending"] = True

            state.approval_status = "pending"

            state.approval_source = (
                "event_selection"
            )

            state.approval_message = (
                "Multiple events matched. "
                "Which event would you like to use?"
            )

            state.next_step = "approval"
            state.next_agent = "approval"

            return state

        if len(matches) == 1:

            state.selected_event = (
                matches[0]
            )

    # --------------------------------------------------
    # SLOT APPROVAL
    # --------------------------------------------------

    if tool_name in {
        "choose_best_slot",
        "find_next_available_day"
    }:

        state.approval_required = True

        state.approval["pending"] = True

        state.approval_status = "pending"

        state.approval_source = (
            "slot_confirmation"
        )

        state.approval_message = (
            "I found a suitable slot. "
            "Would you like me to continue?"
        )

        state.next_step = "approval"
        state.next_agent = "approval"

        return state

    # --------------------------------------------------
    # DESTRUCTIVE ACTION APPROVAL
    # --------------------------------------------------

    if tool_name in APPROVAL_REQUIRED_TOOLS:

        if state.approval_status != "approved":

            state.approval_required = True

            state.approval["pending"] = True

            state.approval_status = "pending"

            state.approval_source = (
                APPROVAL_REQUIRED_TOOLS[
                    tool_name
                ]
            )

            state.approval_message = (
                f"Approve action: {tool_name}?"
            )

            state.next_step = "approval"
            state.next_agent = "approval"

            return state

    # --------------------------------------------------
    # NEXT STEP
    # --------------------------------------------------

    state.current_workflow_step += 1

    if (
        state.current_workflow_step
        >= len(workflow)
    ):

        state.final_response = (
            "Workflow completed successfully."
        )

        state.next_step = "response"
        state.next_agent = "response"

    else:

        state.next_step = "executor"
        state.next_agent = "executor"

    return state



"""import json

from langchain.chat_models import init_chat_model

from config.settings import settings
from agent.state import AgentState
from agent.prompt.executor_prompt import EXECUTOR_PROMPT
from tools.tool_registry import TOOL_REGISTRY


llm = init_chat_model(
    model="gemini-2.5-flash",
    model_provider="google_genai",
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0.1,
    max_tokens=2000,
    max_retries=3
)


def executor_agent(
    state: AgentState
) -> AgentState:

    workflow = state.workflow

    if not workflow:

        state.error = "No workflow found"
        state.next_step = "response"

        return state

    if state.current_workflow_step >= len(workflow):

        state.final_response = (
            "Workflow completed successfully."
        )

        state.next_step = "response"

        return state

    current_step = workflow[
        state.current_workflow_step
    ]

    step_id = current_step["id"]

    tool_name = current_step["tool"]

    params = current_step.get(
        "params",
        {}
    )

    tool = TOOL_REGISTRY.get(
        tool_name
    )

    if not tool:

        state.error = (
            f"Tool not found: {tool_name}"
        )

        state.next_step = "response"

        return state

    try:

        result = tool(
            db=state.db,
            user_id=state.user_id,
            **params
        )

    except Exception as e:

        state.error = str(e)

        state.step_status[
            step_id
        ] = "failed"

        state.next_step = "response"

        return state

    state.step_results[
        step_id
    ] = result

    state.step_status[
        step_id
    ] = "completed"

    prompt = EXECUTOR_PROMPT.format(
        workflow=json.dumps(
            workflow,
            indent=2
        ),
        current_step=json.dumps(
            current_step,
            indent=2
        ),
        tool_name=tool_name,
        tool_result=json.dumps(
            result,
            indent=2,
            default=str
        )
    )

    response = llm.invoke(
        [
            ("system", prompt)
        ]
    )

    content = response.content.strip()

    if content.startswith("```json"):

        content = (
            content
            .replace(
                "```json",
                ""
            )
            .replace(
                "```",
                ""
            )
            .strip()
        )

    try:

        decision = json.loads(
            content
        )

    except Exception:

        state.error = (
            "Executor returned invalid JSON"
        )

        state.next_step = "response"

        return state

    action = decision.get(
        "action"
    )

    if action == "continue":

        state.current_workflow_step += 1

        if (
            state.current_workflow_step
            >= len(workflow)
        ):

            state.final_response = (
                "Workflow completed successfully."
            )

            state.next_step = "response"

        else:

            state.next_step = "executor"

        return state

    if action == "approval":

        state.approval_required = True

        state.approval_status = "pending"

        state.approval_message = (
            decision.get(
                "message"
            )
        )

        state.next_step = "approval"

        return state

    if action == "ask_user":

        state.pending_action = (
            "ask_user"
        )

        state.pending_question = (
            decision.get(
                "message"
            )
        )

        state.next_step = "ask_user"

        return state

    if action == "replan":

        state.user_feedback = (
            decision.get(
                "reason"
            )
        )

        state.plan_history.append(
            state.plan
        )

        state.next_step = "planner"

        return state

    if action == "finish":

        state.final_response = (
            decision.get(
                "message"
            )
        )

        state.next_step = "response"

        return state

    state.error = (
        f"Unknown executor action: {action}"
    )

    state.next_step = "response"

    return state"""