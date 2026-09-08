from agent.planner_agent import planner_agent
from agent.state import AgentState


state = AgentState(
    user_query="Find which event is scheduled at 4 pm today "
     
    
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