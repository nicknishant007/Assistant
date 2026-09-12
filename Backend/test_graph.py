from agent.graph import graph
from agent.state import AgentState
from database.session import SessionLocal


def run_test(
    db,
    user_id: str,
    query: str
):

    state = AgentState(
        db=db,
        user_id=user_id,
        user_query=query
    )

    print("\n" + "=" * 80)
    print("USER QUERY:")
    print(query)
    print("=" * 80)

    final_state = None

    for event in graph.stream(
        state.model_dump(),
        stream_mode="updates"
    ):

        print("\n")
        print("=" * 80)

        for node_name, node_state in event.items():

            print(f"NODE EXECUTED: {node_name}")
            print("-" * 80)

            print("NEXT STEP:")
            print(node_state.get("next_step"))

            print("\nERROR:")
            print(node_state.get("error"))

            print("\nWORKFLOW:")
            print(node_state.get("workflow"))

            print("\nCURRENT WORKFLOW STEP:")
            print(node_state.get("current_workflow_step"))

            print("\nSTEP RESULTS:")
            print(node_state.get("step_results"))

            print("\nVALIDATION:")
            print(node_state.get("validation_result"))

            print("\nFINAL RESPONSE:")
            print(node_state.get("final_response"))

            final_state = node_state

        print("=" * 80)

    print("\n\nFINAL GRAPH STATE")
    print("=" * 80)

    if final_state:
        print("FINAL RESPONSE:")
        print(final_state.get("final_response"))

        print("\nWORKFLOW:")
        print(final_state.get("workflow"))

        print("\nSTEP RESULTS:")
        print(final_state.get("step_results"))

        print("\nVALIDATION:")
        print(final_state.get("validation_result"))

        print("\nERROR:")
        print(final_state.get("error"))

    print("=" * 80)

    return final_state


if __name__ == "__main__":

    run_test(
        db=SessionLocal(),
        user_id="80461e59-6245-4cdb-afb1-354696d8755f",
        query="Scheduke a  agent testing event on 15th from 3 to 5 pm."
    )