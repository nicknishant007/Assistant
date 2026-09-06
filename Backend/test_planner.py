from agent.planner_agent import planner_agent
from agent.state import AgentState


state = AgentState(
    user_query="Can u please reschedule my agent testing event and increase its duration by 2 hours and shift it to the best spot in any of the upcoming 3 day "
    
)

result = planner_agent(
    state=state
)

print("\n========== RESULT ==========")

print("NEXT STEP:")
print(result.next_step)

print("\nAPPROVAL REQUIRED:")
print(result.approval_required)

print("\nAPPROVAL MESSAGE:")
print(result.approval_message)

print("\nPLAN:")
print(result.plan)

print("\nWORKFLOW:")
print(result.workflow)

print("============================\n")