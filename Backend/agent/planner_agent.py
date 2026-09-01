# planner_agent.py

def planner_agent(state):

    query = state.user_query.lower()

    if "schedule" in query:

        state.plan = {
            "tool": "schedule_task"
        }

        state.approval_required = True

    elif "reschedule" in query:

        state.plan = {
            "tool": "reschedule_task"
        }

        state.approval_required = True

    return state