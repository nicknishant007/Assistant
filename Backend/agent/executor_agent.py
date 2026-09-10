from tools.tool_registry import TOOLS
from agent.state import AgentState


APPROVAL_REQUIRED_TOOLS = {

    "delete_task": "delete_event",
    "schedule_task_fixed_time": "schedule_event",
    "schedule_task_auto": "schedule_event",
    "reschedule_task_fixed": "reschedule_event",
    "reschedule_task_day": "reschedule_event",
    "reschedule_task_next_available": "reschedule_event",
}


def resolve(value, step_results):

    if isinstance(value, dict):
        return {
            k: resolve(v, step_results)
            for k, v in value.items()
        }

    if isinstance(value, list):
        return [
            resolve(v, step_results)
            for v in value
        ]

    if (
        isinstance(value, str)
        and value.startswith("{{")
        and value.endswith("}}")
    ):

        path = value[2:-2].strip()

        result = step_results

        for part in path.split("."):
            result = result[part]

        return result

    return value


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
    # WORKFLOW COMPLETE
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

    # --------------------------------------------------
    # RESOLVE PLACEHOLDERS
    # --------------------------------------------------

    resolved_params = resolve(
        params,
        state.step_results
    )

    # --------------------------------------------------
    # FIND TOOL
    # --------------------------------------------------

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

    # --------------------------------------------------
    # EXECUTE TOOL
    # --------------------------------------------------

    try:

        result = tool(
            db=state.db,
            user_id=state.user_id,
            **resolved_params
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

        matches = []

        if result.get("best_match"):
            matches.append(
                result["best_match"]
            )

        matches.extend(
            result.get(
                "alternatives",
                []
            )
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