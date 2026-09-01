# agent/tool_registry.py

from tools.calendar_tool import (
    get_events_tool,
    find_event_by_title_tool
)

from tools.scheduler_tool import (
    schedule_task_tool,
    reschedule_task_tool,
    free_slots_tool,
    delete_task_tool,
    next_available_day_tool
)


TOOLS = {

    "get_events": {
        "function": get_events_tool,

        "description":
            "Retrieve upcoming calendar events.",

        "use_when":
            "User wants to view, list, check, or inspect events.",

        "parameters": {
            "max_results": "int"
        }
    },

    "find_event_by_title": {
        "function": find_event_by_title_tool,

        "description":
            "Search calendar events by title.",

        "use_when":
            "User mentions an event name but not an event ID.",

        "parameters": {
            "title": "str"
        }
    },

    "find_free_slots": {
        "function": free_slots_tool,

        "description":
            "Find all available free time slots on a given date.",

        "use_when":
            "User asks when they are free.",

        "parameters": {
            "date": "datetime"
        }
    },

    "schedule_task": {
        "function": schedule_task_tool,

        "description":
            "Automatically schedule a task into an available slot.",

        "use_when":
            "User wants the system to intelligently place a task into their calendar.",

        "parameters": {
            "title": "str",
            "date": "datetime",
            "duration_minutes": "int"
        }
    },

    "reschedule_task": {
        "function": reschedule_task_tool,

        "description":
            "Move an existing event to the next available time slot.",

        "use_when":
            "User wants to move or reschedule an existing event.",

        "parameters": {
            "event_name": "str",
            "start_date": "datetime",
            "duration_minutes": "int"
        }
    },

    "find_next_available_day": {
        "function": next_available_day_tool,

        "description":
            "Find the next day that has enough free time for a task.",

        "use_when":
            "Today's schedule is full and another day must be searched.",

        "parameters": {
            "start_date": "datetime",
            "duration_minutes": "int"
        }
    },

    "delete_task": {
        "function": delete_task_tool,

        "description":
            "Delete a calendar event using its title.",

        "use_when":
            "User wants to remove, cancel, or delete an event but does not know the event id.",

        "parameters": {
            "title": "str"
        }
    }
    
}