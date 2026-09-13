from pydantic import BaseModel, Field
from typing import Optional, Any


class AgentState(BaseModel):

    # ==================================================
    # USER / SESSION
    # ==================================================

    user_id: Optional[str] = None
    db: Any = None

    conversation_id: Optional[str] = None

    user_query: str

    conversation_history: list[dict] = (
        Field(default_factory=list)
    )

    graph_messages: list[dict] = (
        Field(default_factory=list)
    )

    # ==================================================
    # PLANNER
    # ==================================================

    goal: Optional[str] = None

    plan: Optional[dict] = None

    workflow: list[dict] = (
        Field(default_factory=list)
    )

    plan_history: list[dict] = (
        Field(default_factory=list)
    )

    user_feedback: Optional[str] = None

    # ==================================================
    # EXECUTION
    # ==================================================

    current_workflow_step: int = 0

    step_results: dict = (
        Field(default_factory=dict)
    )

    step_status: dict = (
        Field(default_factory=dict)
    )

    # ==================================================
# EXECUTOR ROUTING
# ==================================================

    next_step: Optional[str] = None

# ==================================================
# APPROVAL FLAGS
# ==================================================

    approval_required: bool = False

    approval_status: Optional[str] = None

    approval_source: Optional[str] = None

    approval_message: Optional[str] = None

    # ==================================================
    # EVENT SELECTION
    # ==================================================

    candidate_events: list[dict] = (
        Field(default_factory=list)
    )

    selected_event: Optional[dict] = None

    # ==================================================
    # SLOT SELECTION
    # ==================================================

    candidate_slots: list[dict] = (
        Field(default_factory=list)
    )

    selected_slot: Optional[dict] = None

    # ==================================================
    # APPROVAL
    # ==================================================

    approval: dict = (
        Field(default_factory=lambda: {
            "pending": False,
            "type": None,
            "step_id": None,
            "message": None,
            "data": None,
            "status": None
        })
    )

    # approval types:
    #
    # event_selection
    # slot_selection
    # delete_confirmation
    # update_confirmation
    # schedule_confirmation

    # ==================================================
    # CLARIFICATION
    # ==================================================

    pending_action: Optional[str] = None

    pending_question: Optional[str] = None

    missing_fields: list[str] = (
        Field(default_factory=list)
    )

    # ==================================================
    # VALIDATION
    # ==================================================

    validation_result: Optional[dict] = None

    # ==================================================
    # RETRIES
    # ==================================================

    retry_count: int = 0

    max_retries: int = 3

    # ==================================================
    # ERROR
    # ==================================================

    error: Optional[str] = None

    # ==================================================
    # RESPONSE
    # ==================================================

    final_response: Optional[str] = None

    # ==================================================
    # GRAPH ROUTING
    # ==================================================

    current_agent: str = "planner"

    next_agent: Optional[str] = None