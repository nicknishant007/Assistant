from agent.planner_agent import planner_agent
from agent.state import AgentState


class Message:

    def __init__(self, role, content):
        self.role = role
        self.content = content


state = AgentState(
    user_query="Reschedule my agent testing meeting to today 7:30 PM",
)

messages = [
    Message(
        role="user",
        content="Reschedule my agent testing meeting to today 7:30 PM"
    )
]

result = planner_agent(
    state=state,
    messages=messages
)

print(result.plan)
print(result.next_step)