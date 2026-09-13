from agent.state import AgentState


def append_message(
    state: AgentState,
    role: str,
    content: str
):

    state.graph_messages.append(
        {
            "role": role,
            "content": content
        }
    )

    return state