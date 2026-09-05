from langgraph.graph import StateGraph
from langgraph.graph import START,END

from agent.state import AgentState

from agent.planner_agent import planner_agent
from agent.approval_node import approval_node
from agent.executor_agent import executor_agent
from agent.validator_agent import validator_agent
from agent.response_agent import response_agent


graph_builder = StateGraph(AgentState)

# NODES
graph_builder.add_node(
    "planner",
    planner_agent
)

graph_builder.add_node(
    "approval",
    approval_node
)

graph_builder.add_node(
    "executor",
    executor_agent
)

graph_builder.add_node(
    "validator",
    validator_agent
)

graph_builder.add_node(
    "response",
    response_agent
)

def approval_router(
    state: AgentState
):
    return state.next_step


def validator_router(
    state: AgentState
):
    return state.next_step


def planner_router(
    state: AgentState
):
    return state.next_step


# GRAPH

graph_builder.add_edge(
    START,"planner")
graph_builder.add_conditional_edges(
    "planner",
    planner_router,
    {
        "approval": "approval",
        "executor": "executor",
        "response": "response"
    }
)

graph_builder.add_conditional_edges(
    "approval",
    approval_router,
    {
        "planner": "planner",
        "executor": "executor",
        "wait_for_approval": END
    }
)

graph_builder.add_edge(
    "executor","validator")
graph_builder.add_conditional_edges(
    "validator",
    validator_router,
    {
        "planner": "planner",
        "response": "response"
    }
)
graph_builder.add_edge(
    "response",
    END
)