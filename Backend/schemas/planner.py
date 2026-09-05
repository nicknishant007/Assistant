from pydantic import BaseModel
from typing import List, Dict, Any


class WorkflowStep(BaseModel):
    id: str
    tool: str
    params: Dict[str, Any]


class PlannerOutput(BaseModel):
    goal: str
    approval_required: bool
    workflow: List[WorkflowStep]