from database.session import SessionLocal

from agent.state import AgentState
from agent.executor_agent import executor_agent

from datetime import datetime


def test_real_executor():

    db = SessionLocal()

    state = AgentState(

        user_id="80461e59-6245-4cdb-afb1-354696d8755f",

        db=db,

        user_query="Reschedule Executor Schedule Test",

        workflow=[

            
    {
        "id": "step_1",
        "tool": "find_event_by_title",
        "params": {
            "title": "Executor Schedule Test"
        }
    },

    {
        "id": "step_2",
        "tool": "find_next_available_day",
        "params": {
            "start_date": datetime.now(),
            "duration_minutes":
                "{{step_1.best_match.duration_minutes}}"
        }
    },

    {
        "id": "step_3",
        "tool": "reschedule_task_next_available",
        "params": {
            "event_id":
                "{{step_1.best_match.event_id}}",

            "title":
                "{{step_1.best_match.title}}",

            "start_datetime":
                "{{step_2.slot.start_datetime}}",

            "end_datetime":
                "{{step_2.slot.end_datetime}}"
        }
    }
]

        
    )

    while True:

        state = executor_agent(state)

        print("\n====================")
        print("CURRENT STEP:", state.current_workflow_step)
        print("NEXT STEP:", state.next_step)
        print("ERROR:", state.error)
        print("STEP STATUS:", state.step_status)

        print("\nSTEP RESULTS:")
        for k, v in state.step_results.items():
            print(k, "=>", v)

        if state.error:
            break

        if state.next_step == "response":
            break

        if state.next_step == "approval":

            print("\nAUTO APPROVING...")

            state.approval_status = "approved"
            state.approval_required = False
            state.approval["pending"] = False

            state.current_workflow_step += 1

            continue

    print("\n===== FINAL =====")
    print("FINAL RESPONSE:", state.final_response)
    print("ERROR:", state.error)

    db.close()


if __name__ == "__main__":
    test_real_executor()