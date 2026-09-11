import json
from datetime import datetime
from zoneinfo import ZoneInfo
from agent.state import AgentState
from agent.prompt.planner_prompt import PLANNER_PROMPT
from tools.tool_registry import get_tool_descriptions
from call_llm import llm




def build_chat_history(history):

    return "\n".join(
        f"{msg['role']}: {msg['content']}"
        for msg in history
    )


def planner_agent(
    state: AgentState
):

    current_datetime = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    prompt = PLANNER_PROMPT.format(
        tool_descriptions=get_tool_descriptions(),
        plan_history=state.plan_history,
        user_feedback=state.user_feedback or "",
        current_datetime=current_datetime.isoformat(),
        timezone="Asia/Kolkata",
        conversation_history=build_chat_history(
            state.conversation_history
        )
    )

    response = llm.invoke(
        [
            ("system", prompt),
            ("user", state.user_query)
        ]
    )

    content = response.content.strip()

    if content.startswith("```json"):
        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

    try:
        result = json.loads(content)

    except Exception as e:

        state.error = (
            f"Planner JSON Parse Error: {e}"
        )

        state.next_step = "error"

        print("\nPlanner Parse Error:")
        print(content)

        return state

    # -------------------------
    # ASK USER FLOW
    # -------------------------

    if result.get("action") == "ask_user":

        state.pending_action = "ask_user"

        state.pending_question = (
            result["message"]
        )

        state.current_step = "planner"

        state.next_step = "ask_user"

        return state

    # -------------------------
    # WORKFLOW FLOW
    # -------------------------

    state.plan = result

    state.workflow = result.get(
        "workflow",
        []
    )

    state.approval_required = result.get(
        "approval_required",
        False
    )

    state.current_workflow_step = 0

    state.current_agent = "planner"

    state.next_step = "executor"

    return state