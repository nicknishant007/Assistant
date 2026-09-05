from tools.tool_registry import TOOLS

from agent.state import AgentState

from agent.utils.variable_resolver import (
    resolve_variables
)


def executor_agent(
    state: AgentState
):

    workflow = state.workflow

    for step in workflow:

        try:

            tool_name = step["tool"]

            tool = TOOLS[
                tool_name
            ]["function"]

            params = resolve_variables(
                step["params"],
                state.step_results
            )

            result = tool(
                db=state.db,
                user_id=state.user_id,
                **params
            )

            state.step_results[
                step["id"]
            ] = result

            state.step_status[
                step["id"]
            ] = "completed"

        except Exception as e:

            state.error = str(e)

            state.step_status[
                step["id"]
            ] = "failed"

            state.next_step = (
                "validator"
            )

            return state

    state.next_step = (
        "validator"
    )

    return state