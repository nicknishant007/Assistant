import json

from langchain.chat_models import init_chat_model
from agent.prompt.planner_prompt import (PLANNER_PROMPT)
from tools.tool_registry import (get_tool_descriptions)
from datetime import datetime
from zoneinfo import ZoneInfo
from agent.state import AgentState

from config.settings import settings


llm = init_chat_model(
    model="gemini-2.5-flash",
    model_provider="google_genai",
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0.1,
    max_tokens=4000,
    max_retries=3
)


def build_chat_history(messages):

    history = []

    for msg in messages:

        history.append(
            (
                msg.role,
                msg.content
            )
        )

    return history


def planner_agent(
    state: AgentState,
    messages
):
    Current_datetime = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    prompt = PLANNER_PROMPT.format(

        tool_descriptions=get_tool_descriptions(),
        plan_history=state.plan_history,
        user_feedback=state.user_feedback,
        current_datetime=Current_datetime.isoformat(),
        timezone="Asia/Kolkata"
    )

    chat_history = build_chat_history(
        messages
    )

    response = llm.invoke(
        [
            ("system", prompt),
            *chat_history
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

        action = plan.get("action")

        if action == "ask_user":

            state.pending_action = (
                "ask_user"
            )

            state.pending_question = (
                plan["message"]
            )

            state.next_step = (
                "ask_user"
            )

            return state

    except Exception as e:

        print("\n========== JSON PARSE ERROR ==========")
        print(content)
        print("======================================\n")

        raise e

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

        state.approval_source = (
            "planner"
        )

        state.approval_message = (
            f"Goal: {plan['goal']}\n\n"
            f"Approve this plan?"
        )

        state.next_step = (
            "approval"
        )

    else:

        state.next_step = (
            "executor"
        )

    print("\n========== PARSED PLAN ==========")
    print(json.dumps(
        state.plan,
        indent=4
    ))
    print("=================================\n")

    return state