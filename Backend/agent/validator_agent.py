def validator_agent(state):

    if state.tool_output:

        state.validation_result = {
            "success": True
        }

    else:

        state.validation_result = {
            "success": False
        }

    return state