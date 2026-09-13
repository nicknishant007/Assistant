from agent.prompt.response_prompt import (
    RESPONSE_PROMPT
)

from agent.state import AgentState
from agent.call_llm import llm
from agent.utils.messages import append_message


def response_agent(
    state: AgentState
) -> AgentState:

    prompt = RESPONSE_PROMPT.format(
        user_query=state.user_query,
        validation_result=state.validation_result,
        step_results=state.step_results,
        error=state.error or "",
        final_response=state.final_response or ""
    )

    response = llm.invoke(
        [
            ("system", prompt),
            ("user", state.user_query)
        ]
    )

    content = (
        response.content
        if hasattr(response, "content")
        else str(response)
    )

    state.final_response = (
        content.strip()
        if content
        else "Sorry, I couldn't generate a response."
    )

    # Save assistant response for DB persistence
    append_message(
        state=state,
        role="assistant",
        content=state.final_response
    )

    state.current_agent = "response"

    # Graph finished
    state.next_agent = None
    state.next_step = None

    return state