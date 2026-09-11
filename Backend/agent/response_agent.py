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
        error=state.error
    )

    response = llm(prompt)

    state.final_response = response

    state.next_step = None
    state.next_agent = None

    return state