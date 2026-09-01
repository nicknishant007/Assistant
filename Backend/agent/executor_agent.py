from agent.tool_registry import TOOLS


def executor_agent(
    state,
    db,
    user_id
):

    tool_name = state.plan["tool"]

    tool = TOOLS[tool_name]

    result = tool(
        db=db,
        user_id=user_id,
        plan=state.plan
    )

    state.tool_output = result

    return state