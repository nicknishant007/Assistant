from agent.state import AgentState


def approval_node(
    state: AgentState
):

    # No approval needed
    if not state.approval_required:

        state.next_step = "executor"

        return state

    # Waiting for user
    if state.approval_status is None:

        state.next_step = (
            "wait_for_approval"
        )

        return state

    # User approved
    if state.approval_status == "approved":

        if (
            state.approval_source
            == "planner"
        ):

            state.next_step = (
                "executor"
            )

        elif (
            state.approval_source
            == "validator"
        ):

            state.next_step = (
                "response"
            )

        return state

    # User rejected
    if state.approval_status == "rejected":

        state.plan_history.append(
            {
                "plan": state.plan,
                "feedback": (
                    state.user_feedback
                )
            }
        )

        state.retry_count += 1

        if (
            state.retry_count
            >= state.max_retries
        ):

            state.error = (
                "Maximum retries reached."
            )

            state.next_step = (
                "response"
            )

            return state

        state.next_step = (
            "planner"
        )

        return state

    return state