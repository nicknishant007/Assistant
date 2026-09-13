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


def planner_router(state: AgentState):
    return state.next_agent or "END"


def executor_router(state: AgentState):
    return state.next_agent or "END"


def validator_router(state: AgentState):
    return state.next_agent or "END"


def response_router(state: AgentState):
    return state.next_agent or "END"

builder.add_edge(
    START,
    "planner"
)

builder.add_conditional_edges(
    "planner",
    planner_router,
    {
        "executor": "executor",
        "response": "response",
        "END": END
    }
)

builder.add_conditional_edges(
    "executor",
    executor_router,
    {
        "executor": "executor",
        "validator": "validator",
        "planner": "planner",
        "response": "response",
        "END": END
    }
)

builder.add_conditional_edges(
    "validator",
    validator_router,
    {
        "planner": "planner",
        "response": "response",
        "END": END
    }
)

builder.add_conditional_edges(
    "response",
    response_router,
    {
        "planner": "planner",
        "END": END
    }
)

graph = builder.compile()