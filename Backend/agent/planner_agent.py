import json
from datetime import datetime
from zoneinfo import ZoneInfo
from langchain.chat_models import init_chat_model
from config.settings import settings
from agent.state import AgentState
from agent.prompt.planner_prompt import PLANNER_PROMPT
from tools.tool_registry import get_tool_descriptions


llm = init_chat_model(
    model="gemini-2.5-flash",
    model_provider="google_genai",
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0.1,
    max_tokens=4000,
    max_retries=3
)

def build_chat_history(history):

    lines = []

    for msg in history:

        lines.append(
            f"{msg['role']}: {msg['content']}"
        )

    return "\n".join(lines)


def planner_agent(
    state: AgentState
):

    current_datetime = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    conversation_history = (
        build_chat_history(
            state.conversation_history
        )
    )

    prompt = PLANNER_PROMPT.format(
        tool_descriptions=get_tool_descriptions(),
        plan_history=state.plan_history,
        user_feedback=state.user_feedback,
        current_datetime=current_datetime.isoformat(),
        timezone="Asia/Kolkata",
        conversation_history=conversation_history
    )

    response = llm.invoke(
        [
            ("system", prompt),
            ("user", state.user_query)
        ]
    )

    print("\n========== RAW LLM RESPONSE ==========")
    print(response.content)
    print("======================================\n")

    content = response.content.strip()

    if content.startswith("```json"):

        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

    try:

        plan = json.loads(content)

    except Exception as e:

        print("\n========== JSON PARSE ERROR ==========")
        print(content)
        print("======================================\n")

        raise e

    if plan.get("action") == "ask_user":

        state.pending_action = "ask_user"

        state.pending_question = (
            plan["message"]
        )

        state.next_step = "ask_user"

        return state

    state.plan = plan

    state.workflow = plan.get(
        "workflow",
        []
    )

    state.approval_required = plan.get(
        "approval_required",
        False
    )

    if state.approval_required:

        state.approval_source = "planner"

        state.approval_message = (
            f"Goal: {plan['goal']}\n\n"
            f"Approve this plan?"
        )

        state.next_step = "approval"

    else:

        state.next_step = "executor"

    print("\n========== PARSED PLAN ==========")

    print(
        json.dumps(
            plan,
            indent=4
        )
    )

    print("=================================\n")

    return state