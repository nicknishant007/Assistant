from agent.state import AgentState
from langsmith import traceable


# ==================================================
# MUTATION TOOLS
# ==================================================

MUTATION_TOOLS = {
    # Calendar
    "schedule_task_auto",
    "schedule_task_fixed_time",
    "reschedule_event",
    "delete_task",

    # Notion
    "notion_create_pages",
    "notion_update_page",
    "notion_create_comment",
}


# ==================================================
# KNOWN MUTATION OUTPUT REQUIREMENTS
# ==================================================
#
# Only add requirements when the tool contract
# is known and stable.
#
# Notion tools are intentionally not forced into
# a particular output structure here because the
# MCP result can contain content / structured data
# depending on the tool.
#
# Generic failure detection below handles them.
# ==================================================

MUTATION_REQUIRED_FIELDS = {

    # Calendar
    "schedule_task_auto": ["event"],
    "schedule_task_fixed_time": ["event"],
    "reschedule_event": ["event"],
    "delete_task": ["event_id"],
}


# ==================================================
# FAILURE DETECTION
# ==================================================

def result_has_failed(result):

    if result is None:
        return True

    if isinstance(result, dict):

        # Common application-level failure
        if result.get("success") is False:
            return True

        # MCP-style error result
        if result.get("is_error") is True:
            return True

        # Generic error field
        if result.get("error"):
            return True

        # Generic status failure
        status = result.get("status")

        if isinstance(status, str):
            if status.lower() in {
                "failed",
                "failure",
                "error",
            }:
                return True

    return False


# ==================================================
# REQUIRED FIELD VALIDATION
# ==================================================

def validate_required_fields(
    result,
    required_fields
):

    if not isinstance(result, dict):

        return False, (
            "Tool result is not a valid object."
        )

    for field in required_fields:

        value = result.get(field)

        if value is None:

            return False, (
                f"Required result field "
                f"'{field}' is missing."
            )

        if value == "":

            return False, (
                f"Required result field "
                f"'{field}' is empty."
            )

    return True, None


# ==================================================
# VALIDATOR
# ==================================================

@traceable(name="validator")
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

    # ==================================================
    # NO WORKFLOW
    # ==================================================

    if not workflow:

        validation_result = {
            "success": False,
            "validated_steps": [],
            "failed_step": None,
            "message": "No workflow found"
        }

        state.validation_result = validation_result

        state.error = (
            validation_result["message"]
        )

        # Let the response agent explain the issue.
        state.next_step = "response"
        state.next_agent = "response"

        return state

    # ==================================================
    # VALIDATE EVERY STEP
    # ==================================================

    for step in workflow:

        step_id = step.get("id")
        tool_name = step.get("tool")

        # ----------------------------------------------
        # INVALID WORKFLOW STEP
        # ----------------------------------------------

        if not step_id or not tool_name:

            validation_result = {
                "success": False,
                "validated_steps": [],
                "failed_step": step_id,
                "message": (
                    "Workflow contains an invalid step."
                )
            }

            break

        # ----------------------------------------------
        # CHECK EXECUTOR STATUS
        # ----------------------------------------------

        step_status = state.step_status.get(
            step_id
        )

        if step_status == "failed":

            validation_result = {
                "success": False,
                "validated_steps": [],
                "failed_step": step_id,
                "message": (
                    f"Execution failed for "
                    f"{step_id}."
                )
            }

            break

        # ----------------------------------------------
        # GET RESULT
        # ----------------------------------------------

        result = state.step_results.get(
            step_id
        )

        if result is None:

            validation_result = {
                "success": False,
                "validated_steps": [],
                "failed_step": step_id,
                "message": (
                    f"No result found for {step_id}"
                )
            }

            break

        # ----------------------------------------------
        # GENERIC FAILURE CHECK
        # ----------------------------------------------

        if result_has_failed(result):

            validation_result = {
                "success": False,
                "validated_steps": [],
                "failed_step": step_id,
                "message": (
                    f"Tool execution failed for "
                    f"{tool_name}"
                )
            }

            break

        # ----------------------------------------------
        # MUTATION VALIDATION
        # ----------------------------------------------

        if tool_name in MUTATION_TOOLS:

            required_fields = (
                MUTATION_REQUIRED_FIELDS.get(
                    tool_name
                )
            )

            if required_fields:

                valid, message = (
                    validate_required_fields(
                        result,
                        required_fields
                    )
                )

                if not valid:

                    validation_result = {
                        "success": False,
                        "validated_steps": [],
                        "failed_step": step_id,
                        "message": (
                            f"{tool_name}: "
                            f"{message}"
                        )
                    }

                    break

        # ----------------------------------------------
        # STEP VALIDATED
        # ----------------------------------------------

        validation_result[
            "validated_steps"
        ].append(step_id)

    # ==================================================
    # SAVE VALIDATION RESULT
    # ==================================================

    state.validation_result = validation_result

    # ==================================================
    # VALIDATION SUCCESS
    # ==================================================

    if validation_result["success"]:

        state.error = None

        state.next_step = "response"
        state.next_agent = "response"

        return state

    # ==================================================
    # VALIDATION FAILURE
    # ==================================================

    state.error = (
        validation_result["message"]
    )

    # ----------------------------------------------
    # RETRY / REPLAN
    # ----------------------------------------------

    state.retry_count += 1

    if state.retry_count < state.max_retries:

        state.next_step = "planner"
        state.next_agent = "planner"

        return state

    # ----------------------------------------------
    # MAX RETRIES REACHED
    # ----------------------------------------------

    state.next_step = "response"
    state.next_agent = "response"

    return state