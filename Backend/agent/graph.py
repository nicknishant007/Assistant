from langgraph.graph import (StateGraph,START,END)
from agent.state import AgentState
from agent.planner_agent import planner_agent
from agent.notionplanner_agent import notion_planner_agent
from agent.notionexecutor_agent import notion_executor_agent
from agent.calplanner_agent import cal_planner_agent
from agent.calexecutor_agent import cal_executor_agent
from agent.validator_agent import validator_agent
from agent.response_agent import response_agent


builder = StateGraph(AgentState)

builder.add_node(
    "planner",
    planner_agent
)

builder.add_node(
    "calendar_planner",
    cal_planner_agent
)

builder.add_node(
    "notion_planner",
    notion_planner_agent
)

builder.add_node(
    "calendar_executor",
    cal_executor_agent
)

builder.add_node(
    "notion_executor",
    notion_executor_agent
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


def calendar_planner_router(state: AgentState):

    return state.next_agent or "END"


def notion_planner_router(state: AgentState):

    return state.next_agent or "END"


def calendar_executor_router(state: AgentState):

    return state.next_agent or "END"


def notion_executor_router(state: AgentState):

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
        "calendar_planner": "calendar_planner",
        "notion_planner": "notion_planner",
        "response": "response",
        "END": END
    }
)


builder.add_conditional_edges(
    "calendar_planner",
    calendar_planner_router,
    {
        "calendar_executor": "calendar_executor",
        "response": "response",
        "END": END
    }
)



builder.add_conditional_edges(
    "notion_planner",
    notion_planner_router,
    {
        "notion_executor": "notion_executor",
        "response": "response",
        "END": END
    }
)



builder.add_conditional_edges(
    "calendar_executor",
    calendar_executor_router,
    {
        "calendar_executor": "calendar_executor",
        "validator": "validator",
        "planner": "planner",
        "response": "response",
        "END": END
    }
)



builder.add_conditional_edges(
    "notion_executor",
    notion_executor_router,
    {
        "notion_executor": "notion_executor",
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