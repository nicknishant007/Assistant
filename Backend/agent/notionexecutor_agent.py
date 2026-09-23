import re

from tools.notiontool_registry import TOOLS
from agent.state import AgentState
from langsmith import traceable


# ============================================================
# RESOLVE PATH
# ============================================================

PATH_PATTERN = re.compile(
    r"([^[.\]]+)|\[(\d+)\]"
)


def resolve_path(
    path: str,
    step_results: dict,
):
    """
    Resolve paths such as:

        step_1.results[0].id
        step_2.data_sources[0].url
    """

    result = step_results

    tokens = []

    for match in PATH_PATTERN.finditer(path):

        key = match.group(1)
        index = match.group(2)

        if key is not None:
            tokens.append(key)

        elif index is not None:
            tokens.append(int(index))

    for token in tokens:

        if isinstance(token, int):

            if not isinstance(result, list):
                raise TypeError(
                    f"Expected list while resolving "
                    f"[{token}], got "
                    f"{type(result).__name__}"
                )

            result = result[token]

        else:

            if not isinstance(result, dict):
                raise TypeError(
                    f"Expected dict while resolving "
                    f"'{token}', got "
                    f"{type(result).__name__}"
                )

            result = result[token]

    return result


# ============================================================
# RESOLVE WORKFLOW VALUES
# ============================================================

def resolve(
    value,
    step_results,
):
    """
    Recursively resolve workflow placeholders.
    """

    if isinstance(value, dict):

        return {
            key: resolve(
                item,
                step_results,
            )
            for key, item in value.items()
        }

    if isinstance(value, list):

        return [
            resolve(
                item,
                step_results,
            )
            for item in value
        ]

    if (
        isinstance(value, str)
        and value.startswith("{{")
        and value.endswith("}}")
    ):

        path = value[2:-2].strip()

        return resolve_path(
            path,
            step_results,
        )

    return value


# ============================================================
# NOTION EXECUTOR
# ============================================================

@traceable(name="notion_executor_agent")
def notion_executor_agent(
    state: AgentState,
) -> AgentState:

    workflow = state.workflow

    print("\nWORKFLOW:")
    print(workflow)

    # --------------------------------------------------------
    # NO WORKFLOW
    # --------------------------------------------------------

    if not workflow:

        state.error = "No workflow found"

        state.next_step = "validator"
        state.next_agent = "validator"

        return state

    # --------------------------------------------------------
    # WORKFLOW COMPLETE
    # --------------------------------------------------------

    if (
        state.current_workflow_step
        >= len(workflow)
    ):

        state.next_step = "validator"
        state.next_agent = "validator"

        return state

    # --------------------------------------------------------
    # CURRENT STEP
    # --------------------------------------------------------

    current_step = workflow[
        state.current_workflow_step
    ]

    step_id = current_step["id"]

    tool_name = current_step["tool"]

    params = current_step.get(
        "params",
        {},
    )

    print(
        "\n========== NOTION EXECUTOR =========="
    )
    print("STEP ID:", step_id)
    print("TOOL:", tool_name)
    print("RAW PARAMS:", params)
    print("STEP RESULTS:", state.step_results)

    # --------------------------------------------------------
    # RESOLVE PARAMETERS
    # --------------------------------------------------------

    try:

        resolved_params = resolve(
            params,
            state.step_results,
        )

        print(
            "RESOLVED PARAMS:",
            resolved_params,
        )

    except Exception as e:

        print(
            "\n[NOTION PARAMETER ERROR]",
            repr(e),
        )

        state.error = (
            f"Parameter resolution failed: {str(e)}"
        )

        state.step_status[
            step_id
        ] = "failed"

        state.next_step = "validator"
        state.next_agent = "validator"

        return state

    # --------------------------------------------------------
    # FIND TOOL
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # GET EXECUTABLE FUNCTION
    # --------------------------------------------------------

    tool = tool_meta.get(
        "function"
    )

    if tool is None:

        state.error = (
            f"No executable function for tool: "
            f"{tool_name}"
        )

        state.step_status[
            step_id
        ] = "failed"

        state.next_step = "validator"
        state.next_agent = "validator"

        return state

    # --------------------------------------------------------
    # EXECUTE TOOL
    # --------------------------------------------------------

    try:

        result = tool(
            db=state.db,
            user_id=state.user_id,
            **resolved_params,
        )

    except Exception as e:

        print(
            "\n========== NOTION TOOL ERROR =========="
        )
        print("STEP ID:", step_id)
        print("TOOL:", tool_name)
        print(
            "ERROR TYPE:",
            type(e).__name__,
        )
        print(
            "ERROR:",
            repr(e),
        )

        import traceback

        traceback.print_exc()

        state.error = str(e)

        state.step_status[
            step_id
        ] = "failed"

        state.next_step = "validator"
        state.next_agent = "validator"

        return state

    # --------------------------------------------------------
    # SAVE RESULT
    # --------------------------------------------------------

    print(
        "\n========== NOTION TOOL RESULT =========="
    )
    print("STEP ID:", step_id)
    print("TOOL:", tool_name)
    print("RESULT:", result)

    state.step_results[
        step_id
    ] = result

    state.step_status[
        step_id
    ] = "completed"

    # --------------------------------------------------------
    # ADVANCE WORKFLOW
    # --------------------------------------------------------

    state.current_workflow_step += 1

    # --------------------------------------------------------
    # MORE STEPS
    # --------------------------------------------------------

    if (
        state.current_workflow_step
        < len(workflow)
    ):

        state.next_step = "notion_executor"
        state.next_agent = "notion_executor"

        return state

    # --------------------------------------------------------
    # WORKFLOW FINISHED
    # --------------------------------------------------------

    state.next_step = "validator"
    state.next_agent = "validator"

    return state