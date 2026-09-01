def response_agent(state):

    if (
        state.validation_result
        and
        state.validation_result["success"]
    ):
        state.final_response = (
            "Task completed successfully"
        )

    else:
        state.final_response = (
            "Task failed"
        )

    return state