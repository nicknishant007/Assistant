import json
from datetime import datetime
from zoneinfo import ZoneInfo

from agent.state import AgentState
from agent.prompt.notionplanner_prompt import NOTIONPLANNER_PROMPT
from tools.notiontool_registry import get_tool_descriptions
from agent.call_llm import llm


def build_chat_history(history):
    return "\n".join(
        f"{msg['role']}: {msg['content']}"
        for msg in history
    )


def main():
    # --------------------------------------------------
    # TEST QUERY
    # --------------------------------------------------
    user_query = (
        'Find my Notion database called "Companies I have applied". '
        'If there are multiple results, choose the exact title match. '
        'Open the database and tell me which companies are currently listed. '
        'Do not modify anything.'
    )

    # --------------------------------------------------
    # MINIMAL STATE NEEDED BY NOTION PLANNER
    # --------------------------------------------------
    state = AgentState(
        user_query=user_query,
        conversation_history=[],
        plan_history=[],
        user_feedback=None,
        context={},
        validation_result=None,
    )

    current_datetime = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    # --------------------------------------------------
    # BUILD THE EXACT SAME PROMPT USED BY THE AGENT
    # --------------------------------------------------
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
            state.validation_result or {}
        ),
    )

    print("\n")
    print("=" * 90)
    print("NOTION PLANNER LLM TEST")
    print("=" * 90)
    print("USER QUERY:")
    print(user_query)

    print("\n")
    print("=" * 90)
    print("SYSTEM PROMPT")
    print("=" * 90)
    print(prompt)

    # --------------------------------------------------
    # RAW LLM CALL
    # --------------------------------------------------
    print("\n")
    print("=" * 90)
    print("CALLING LLM...")
    print("=" * 90)

    try:
        response = llm.invoke(
            [
                ("system", prompt),
                ("user", user_query),
            ]
        )

    except Exception as exc:
        print("\nLLM CALL FAILED")
        print("TYPE:", type(exc).__name__)
        print("ERROR:", repr(exc))
        raise

    # --------------------------------------------------
    # FULL LLM RESPONSE OBJECT
    # --------------------------------------------------
    print("\n")
    print("=" * 90)
    print("FULL LLM RESPONSE OBJECT")
    print("=" * 90)
    print(response)

    # --------------------------------------------------
    # RAW CONTENT
    # --------------------------------------------------
    content = response.content

    print("\n")
    print("=" * 90)
    print("RAW RESPONSE.CONTENT")
    print("=" * 90)
    print(repr(content))

    print("\n")
    print("=" * 90)
    print("RESPONSE.CONTENT (NORMAL)")
    print("=" * 90)
    print(content)

    # --------------------------------------------------
    # RESPONSE METADATA
    # --------------------------------------------------
    print("\n")
    print("=" * 90)
    print("RESPONSE METADATA")
    print("=" * 90)
    print(response.response_metadata)

    print("\n")
    print("=" * 90)
    print("ADDITIONAL KWARGS")
    print("=" * 90)
    print(response.additional_kwargs)

    print("\n")
    print("=" * 90)
    print("USAGE METADATA")
    print("=" * 90)
    print(getattr(response, "usage_metadata", None))

    print("\n")
    print("=" * 90)
    print("TOOL CALLS")
    print("=" * 90)
    print(getattr(response, "tool_calls", None))

    # --------------------------------------------------
    # TRY THE SAME JSON CLEANUP/PARSE AS THE REAL AGENT
    # --------------------------------------------------
    cleaned_content = content.strip()

    if cleaned_content.startswith("```json"):
        cleaned_content = (
            cleaned_content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

    elif cleaned_content.startswith("```"):
        cleaned_content = (
            cleaned_content
            .replace("```", "")
            .strip()
        )

    print("\n")
    print("=" * 90)
    print("CLEANED CONTENT USED FOR JSON PARSING")
    print("=" * 90)
    print(repr(cleaned_content))

    print("\n")
    print("=" * 90)
    print("PARSED JSON")
    print("=" * 90)

    try:
        result = json.loads(cleaned_content)
        print(json.dumps(result, indent=2, ensure_ascii=False))

        print("\n")
        print("=" * 90)
        print("WORKFLOW SUMMARY")
        print("=" * 90)

        workflow = result.get("workflow", [])

        print("workflow steps:", len(workflow))
        print("approval_required:", result.get("approval_required"))
        print("approval_message:", result.get("approval_message"))
        print("pending_question:", result.get("pending_question"))

        for index, step in enumerate(workflow, start=1):
            print(f"\nSTEP {index}")
            print("id:", step.get("id"))
            print("tool:", step.get("tool"))
            print(
                "params:",
                json.dumps(
                    step.get("params", {}),
                    indent=2,
                    ensure_ascii=False,
                ),
            )

    except json.JSONDecodeError as exc:
        print("JSON PARSE FAILED")
        print("ERROR:", repr(exc))


if __name__ == "__main__":
    main()

