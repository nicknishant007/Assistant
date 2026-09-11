from tools.tool_registry import TOOLS
from agent.state import AgentState


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

        state.next_step = "validator"
        state.next_agent = "validator"

        return state

    # --------------------------------------------------
    # WORKFLOW COMPLETE
    # --------------------------------------------------

    if state.current_workflow_step >= len(workflow):

        state.next_step = "validator"
        state.next_agent = "validator"

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

    try:

        resolved_params = resolve(
            params,
            state.step_results
        )

    except Exception as e:

        state.error = (
            f"Parameter resolution failed: {str(e)}"
        )

        state.step_status[
            step_id
        ] = "failed"

        state.next_step = "validator"
        state.next_agent = "validator"

        return state

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

        state.step_status[
            step_id
        ] = "failed"

        state.next_step = "validator"
        state.next_agent = "validator"

        return state

    tool = tool_meta.get(
        "function"
    )

    if tool is None:

        state.error = (
            f"No executable function for tool: {tool_name}"
        )

        state.step_status[
            step_id
        ] = "failed"

        state.next_step = "validator"
        state.next_agent = "validator"

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

        state.next_step = "validator"
        state.next_agent = "validator"

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
    # ADVANCE WORKFLOW
    # --------------------------------------------------

    state.current_workflow_step += 1

    # --------------------------------------------------
    # MORE STEPS REMAIN
    # --------------------------------------------------

    if (
        state.current_workflow_step
        < len(workflow)
    ):

        state.next_step = "executor"
        state.next_agent = "executor"

        return state

    # --------------------------------------------------
    # WORKFLOW FINISHED
    # --------------------------------------------------

    state.next_step = "validator"
    state.next_agent = "validator"

    return state