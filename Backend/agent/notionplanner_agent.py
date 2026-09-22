import json
from datetime import datetime
from zoneinfo import ZoneInfo

from langsmith import traceable

from agent.state import AgentState
from agent.prompt.notionplanner_prompt import NOTIONPLANNER_PROMPT
from tools.notiontool_registry import get_tool_descriptions
from agent.call_llm import llm
from agent.utils.messages import append_message


def build_chat_history(history):

    return "\n".join(
        f"{msg['role']}: {msg['content']}"
        for msg in history
    )


@traceable(name="notion_planner_agent")
def notion_planner_agent(
    state: AgentState
):

    # ==========================================
    # CURRENT DATETIME
    # ==========================================

    current_datetime = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    # ==========================================
    # BUILD PROMPT
    # ==========================================

    prompt = NOTIONPLANNER_PROMPT.format(
        tool_descriptions=get_tool_descriptions(),

        current_datetime=current_datetime.isoformat(),

        timezone="Asia/Kolkata",

        conversation_history=build_chat_history(
            state.conversation_history
        ),

        plan_history=state.plan_history,

        user_feedback=state.user_feedback or "",

        context=state.context,

        validation_result=(
            state.validation_result
            or {}
        )
    )

    # ==========================================
    # CALL LLM
    # ==========================================

    response = llm.invoke(
        [
            ("system", prompt),
            ("user", state.user_query)
        ]
    )

    content = response.content.strip()

    # ==========================================
    # CLEAN JSON
    # ==========================================

    if content.startswith("```json"):

        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

    elif content.startswith("```"):

        content = (
            content
            .replace("```", "")
            .strip()
        )

    # ==========================================
    # PARSE JSON
    # ==========================================

    try:

        result = json.loads(content)

    except Exception as e:

        state.error = (
            f"Notion Planner JSON Parse Error: {e}"
        )

        state.final_response = (
            "I couldn't understand the Notion request."
        )

        append_message(
            state,
            "assistant",
            state.final_response
        )

        state.next_agent = None

        return state

    # ==========================================
    # SAVE PLAN
    # ==========================================

    state.plan = result

    state.workflow = result.get(
        "workflow",
        []
    )

    state.approval_required = result.get(
        "approval_required",
        False
    )

    state.approval_message = result.get(
        "approval_message"
    )

    state.current_workflow_step = 0

    state.current_agent = "notion_planner"

    # ==========================================
    # CLARIFICATION QUESTION
    # ==========================================

    if result.get("pending_question"):

        state.pending_question = (
            result["pending_question"]
        )

        append_message(
            state,
            "assistant",
            state.pending_question
        )

        state.next_agent = None

        return state

    # ==========================================
    # APPROVAL REQUEST
    # ==========================================

    if result.get("approval_message"):

        append_message(
            state,
            "assistant",
            state.approval_message
        )

        state.next_agent = None

        return state

    # ==========================================
    # NO WORKFLOW
    # ==========================================

    if not state.workflow:

        state.goal = result.get(
            "goal",
            state.user_query
        )

        state.next_agent = "response"

        return state

    # ==========================================
    # EXECUTE NOTION WORKFLOW
    # ==========================================

    state.next_agent = "notion_executor"

    return state