from agent.state import AgentState


def validator_agent(
    state: AgentState
):

    # Executor error
    if state.error:

        state.validation_result = {
            "success": False,
            "reason": state.error
        }

        if (
            state.retry_count
            >= state.max_retries
        ):

            state.next_step = (
                "response"
            )

            return state

        state.next_step = (
            "planner"
        )

        return state

    # Failed steps
    failed_steps = [

        step_id

        for step_id, status

        in state.step_status.items()

        if status == "failed"
    ]

    if failed_steps:

        state.validation_result = {
            "success": False,
            "failed_steps": failed_steps
        }

        state.next_step = (
            "planner"
        )

        return state

    # No workflow executed
    if not state.step_results:

        state.validation_result = {
            "success": False,
            "reason": "No tool executed"
        }

        state.next_step = (
            "planner"
        )

        return state

    state.validation_result = {
        "success": True
    }

    state.next_step = (
        "response"
    )

    return state