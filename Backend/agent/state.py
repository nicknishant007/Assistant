from typing import Optional


class AgentState:

    def __init__(
        self,
        user_query: str
    ):
        self.user_query = user_query

        # planning
        self.plan = None
        self.plan_history = []

        # human approval
        self.approval_required = False
        self.approval_status = "pending"

        # feedback
        self.user_feedback = None

        # execution
        self.tool_output = None

        # validation
        self.validation_result = None

        # response
        self.final_response = None