from agent.state import AgentState


def response_agent(
    state: AgentState
):

    # Approval message
    if (
        state.next_step
        == "wait_for_approval"
    ):

        state.final_response = (
            state.approval_message
        )

        return state

    # Error response
    if state.error:

        state.final_response = (
            f"Request failed.\n\n"
            f"Reason: {state.error}"
        )

        return state

    # Validation failure
    if (
        state.validation_result
        and not state.validation_result.get(
            "success",
            False
        )
    ):

        reason = (
            state.validation_result.get(
                "reason",
                "Unknown error"
            )
        )

        state.final_response = (
            f"Request failed.\n\n"
            f"Reason: {reason}"
        )

        return state

    # Success
    state.final_response = (
        "Task completed successfully.\n\n"
        f"Executed {len(state.step_results)} step(s)."
    )

    return state