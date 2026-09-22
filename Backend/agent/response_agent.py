from agent.prompt.response_prompt import (RESPONSE_PROMPT)
from langsmith import traceable
from agent.state import AgentState
from agent.call_llm import llm
from agent.utils.messages import append_message


@traceable(name="response_agent")
def response_agent(
    state: AgentState
) -> AgentState:

    # ==========================================
    # BUILD PROMPT
    # ==========================================

    prompt = RESPONSE_PROMPT.format(

        user_query=state.user_query,

        validation_result=(
            state.validation_result
            or {}
        ),

        step_results=(
            state.step_results
            or {}
        ),

        error=(
            state.error
            or ""
        ),

        final_response=(
            state.final_response
            or ""
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

    print(response)

    # ==========================================
    # EXTRACT CONTENT
    # ==========================================

    content = (
        response.content
        if hasattr(response, "content")
        else str(response)
    )

    state.final_response = (
        content.strip()
        if content
        else (
            "Sorry, I couldn't generate "
            "a response."
        )
    )

    # ==========================================
    # SAVE ASSISTANT RESPONSE
    # ==========================================

    append_message(
        state=state,
        role="assistant",
        content=state.final_response
    )

    # ==========================================
    # FINISH GRAPH
    # ==========================================

    state.current_agent = "response"

    state.next_agent = None
    state.next_step = None

    return state