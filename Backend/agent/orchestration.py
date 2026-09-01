from agent.state import AgentState

from agent.planner_agent import (
    planner_agent
)

from agent.executor_agent import (
    executor_agent
)

from agent.validator_agent import (
    validator_agent
)

from agent.response_agent import (
    response_agent
)


def run_agent(
    query: str,
    db,
    user_id: str
):

    state = AgentState(
        user_query=query
    )

    planner_agent(state)

    # HITL
    if state.approval_required:

        return {
            "status": "approval_required",
            "plan": state.plan
        }

    executor_agent(
        state,
        db,
        user_id
    )

    validator_agent(state)

    response_agent(state)

    return state.final_response