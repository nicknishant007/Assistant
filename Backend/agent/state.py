from pydantic import BaseModel, Field
from typing import Optional, Any


class AgentState(BaseModel):

    # Runtime
    user_id: Optional[str] = None
    db: Any = None

    # Current user message
    user_query: str

    # Conversation
    conversation_id: Optional[str] = None

    conversation_history: list[dict] = (
        Field(default_factory=list)
    )

    # Planner
    plan: Optional[dict] = None
    workflow: list[dict] = (
        Field(default_factory=list)
    )

    # Clarification Flow
    pending_action: Optional[str] = None

    pending_question: Optional[str] = None

    missing_fields: list[str] = (
        Field(default_factory=list)
    )

    # Event Selection
    candidate_events: list[dict] = (
        Field(default_factory=list)
    )

    selected_event: Optional[dict] = None

    # Workflow Execution
    current_workflow_step: int = 0

    step_results: dict = (
        Field(default_factory=dict)
    )

    step_status: dict = (
        Field(default_factory=dict)
    )

    # Approval
    approval_required: bool = False

    approval_source: Optional[str] = None

    approval_status: Optional[str] = None

    approval_message: Optional[str] = None

    # Replanning
    plan_history: list[dict] = (
        Field(default_factory=list)
    )

    user_feedback: Optional[str] = None

    # Validation
    validation_result: Optional[dict] = None

    # Retry
    retry_count: int = 0
    max_retries: int = 3

    # Error
    error: Optional[str] = None

    # Response
    final_response: Optional[str] = None

    # Graph Routing
    current_step: str = "planner"

    next_step: Optional[str] = None