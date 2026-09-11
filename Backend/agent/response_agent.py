from prompt.response_prompt import (
    RESPONSE_PROMPT
)

from agent.state import AgentState
from call_llm import llm


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
            ("system", prompt)
        ]
    )

    if hasattr(response, "content"):
        state.final_response = response.content
    else:
        state.final_response = str(response)

    state.current_agent = "response"
    state.next_agent = None
    state.next_step = None

    return state