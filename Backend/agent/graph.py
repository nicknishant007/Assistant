from langgraph.graph import (
    StateGraph,
    START,
    END
)

from agent.state import AgentState

from agent.planner_agent import planner_agent
from agent.executor_agent import executor_agent
from agent.validator_agent import validator_agent
from agent.response_agent import response_agent


builder = StateGraph(AgentState)

# --------------------------------------------------
# NODES
# --------------------------------------------------

builder.add_node(
    "planner",
    planner_agent
)

builder.add_node(
    "executor",
    executor_agent
)

builder.add_node(
    "validator",
    validator_agent
)

builder.add_node(
    "response",
    response_agent
)

# --------------------------------------------------
# ROUTERS
# --------------------------------------------------

def planner_router(
    state: AgentState
):
    return state.next_step


def executor_router(
    state: AgentState
):
    return state.next_step


def validator_router(
    state: AgentState
):
    return state.next_step


# --------------------------------------------------
# FLOW
# --------------------------------------------------

builder.add_edge(
    START,
    "planner"
)

builder.add_conditional_edges(
    "planner",
    planner_router,
    {
        "executor": "executor",
        "response": "response"
    }
)

builder.add_conditional_edges(
    "executor",
    executor_router,
    {
        "executor": "executor",
        "validator": "validator",
        "response": "response"
    }
)

builder.add_conditional_edges(
    "validator",
    validator_router,
    {
        "planner": "planner",
        "response": "response"
    }
)

builder.add_edge(
    "response",
    END
)

graph = builder.compile()