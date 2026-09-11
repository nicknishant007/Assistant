from agent.state import AgentState


MUTATION_TOOLS = {
    "schedule_task_auto",
    "schedule_task_fixed_time",
    "reschedule_event",
    "delete_task"
}


def validator_agent(
    state: AgentState
) -> AgentState:

    validation_result = {
        "success": True,
        "validated_steps": [],
        "failed_step": None,
        "message": "Validation passed"
    }

    workflow = state.workflow

    for step in workflow:

        tool_name = step["tool"]
        step_id = step["id"]

        # ----------------------------------
        # Ignore read-only tools
        # ----------------------------------

        if tool_name not in MUTATION_TOOLS:
            continue

        result = state.step_results.get(step_id)

        if result is None:

            validation_result = {
                "success": False,
                "validated_steps": [],
                "failed_step": step_id,
                "message": f"No result found for {step_id}"
            }

            break

        # ----------------------------------
        # SCHEDULE
        # ----------------------------------

        if tool_name in {
            "schedule_task_auto",
            "schedule_task_fixed_time"
        }:

            if not result.get("success"):

                validation_result = {
                    "success": False,
                    "validated_steps": [],
                    "failed_step": step_id,
                    "message": "Event scheduling failed"
                }

                break

            event = result.get("event")

            if not event:

                validation_result = {
                    "success": False,
                    "validated_steps": [],
                    "failed_step": step_id,
                    "message": "Scheduled event missing"
                }

                break

            validation_result[
                "validated_steps"
            ].append(step_id)

        # ----------------------------------
        # RESCHEDULE
        # ----------------------------------

        elif tool_name == "reschedule_event":

            if not result.get("success"):

                validation_result = {
                    "success": False,
                    "validated_steps": [],
                    "failed_step": step_id,
                    "message": "Event reschedule failed"
                }

                break

            event = result.get("event")

            if not event:

                validation_result = {
                    "success": False,
                    "validated_steps": [],
                    "failed_step": step_id,
                    "message": "Updated event missing"
                }

                break

            validation_result[
                "validated_steps"
            ].append(step_id)

        # ----------------------------------
        # DELETE
        # ----------------------------------

        elif tool_name == "delete_task":

            if not result.get("success"):

                validation_result = {
                    "success": False,
                    "validated_steps": [],
                    "failed_step": step_id,
                    "message": "Event deletion failed"
                }

                break

            if not result.get("event_id"):

                validation_result = {
                    "success": False,
                    "validated_steps": [],
                    "failed_step": step_id,
                    "message": "Deleted event id missing"
                }

                break

            validation_result[
                "validated_steps"
            ].append(step_id)

    # ----------------------------------
    # Save validation result
    # ----------------------------------

    state.validation_result = validation_result

    if validation_result["success"]:

        state.final_response = (
            "Workflow executed and validated successfully."
        )

    else:

        state.error = validation_result["message"]

        state.final_response = (
            f"Validation failed: "
            f"{validation_result['message']}"
        )

    state.next_step = "response"
    state.next_agent = "response"

    return state