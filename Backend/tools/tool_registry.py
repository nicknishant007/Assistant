from tools.calendar_tool import (
    get_events_tool,
    find_event_by_title_tool
)

from tools.scheduler_tool import (
    schedule_task_fixed_tool,
    schedule_task_auto_tool,
    reschedule_task_fixed_tool,
    reschedule_task_day_tool,
    reschedule_task_next_available_tool,
    choose_best_slot_tool,
    free_slots_tool,
    delete_task_tool,
    next_available_day_tool
)


TOOLS = {

"get_events": {
    "function": get_events_tool,

    "description":
        """
        Retrieve upcoming calendar events.
        """,

    "use_when":
        """
        Use when:
        - User wants to view events.
        - User asks for today's schedule.
        - User asks for upcoming meetings.
        - User wants to inspect calendar events.
        - User wants to know what is scheduled.
        """,

    "prerequisite_tools": [],

    "input_parameters": {
        "max_results": "int"
    },

    "output": {
        "events": [
            {
                "event_id": "str",
                "title": "str",
                "start_time": "datetime",
                "end_time": "datetime"
            }
        ]
    },

    "example_output": [
        {
            "event_id": "abc123",
            "title": "Team Sync",
            "start_time": "2026-09-10T10:00:00",
            "end_time": "2026-09-10T11:00:00"
        }
    ]
},
"find_event_by_title": {
    "function": find_event_by_title_tool,

    "description":
        """
        Search calendar events using an event title
        and return the most likely matching event
        along with alternative matches.
        """,

    "use_when":
        """
        Use when:
        - User mentions an event name.
        - User wants to update an event.
        - User wants to reschedule an event.
        - User wants to delete an event.
        - Event details are required for later workflow steps.
        - Event duration is required for later workflow steps.
        """,

    "prerequisite_tools": [],

    "input_parameters": {
        "title": "str",
        "date": "str (optional)",
        "day": "str (optional)"
    },

    "output": {

        "found": "bool",

        "best_match": {
            "event_id": "str",
            "title": "str",
            "start_time": "datetime",
            "end_time": "datetime",
            "duration_minutes": "int",
            "score": "float"
        },

        "alternatives": [
            {
                "event_id": "str",
                "title": "str",
                "start_time": "datetime",
                "end_time": "datetime",
                "duration_minutes": "int",
                "score": "float"
            }
        ]
    },

    "example_output": {

        "found": True,

        "best_match": {
            "event_id": "abc123",
            "title": "Team Sync",
            "start_time": "2026-09-10T10:00:00",
            "end_time": "2026-09-10T11:00:00",
            "duration_minutes": 60,
            "score": 100
        },

        "alternatives": [
            {
                "event_id": "xyz456",
                "title": "Team Sync Weekly",
                "start_time": "2026-09-12T14:00:00",
                "end_time": "2026-09-12T15:00:00",
                "duration_minutes": 60,
                "score": 80
            }
        ]
    }
},

"find_free_slots": {
    "function": free_slots_tool,

    "description":
        """
        Find all available free time slots for a specific date
        based on existing calendar events and user preferences.
        """,

    "use_when":
        """
        - User asks when they are free.
        - User wants available meeting times.
        - Need available slots before scheduling.
        - Need available slots before moving an event.
        """,

    "input_parameters": {
        "date": "datetime",
    },

    "output": {
        "free_slots": [
            {
                "start_time": "time",
                "end_time": "time"
            }
        ]
    },

    "prerequisites":
        """
        Requires a valid date.
        Does not require event_id.
        Can be called directly.
        """,

    "next_possible_tools": [
        "schedule_task",
        "update_event",
        "reschedule_task"
    ],

    "example_output": [
        {
            "start_time": "09:00",
            "end_time": "11:00"
        },
        {
            "start_time": "14:00",
            "end_time": "16:30"
        }
    ]
},

"choose_best_slot": {

    "function": choose_best_slot_tool,

    "description":
        """
        Select the earliest available free slot that can
        accommodate the requested duration.
        """,

    "use_when":
        """
        - After find_free_slots returns available slots.
        - Before scheduling a new event.
        - Before rescheduling an existing event.
        - When a duration is known and the best slot
          must be chosen.
        """,

    "input_parameters": {
        "free_slots": [
            {
                "start_time": "time",
                "end_time": "time"
            }
        ],
        "date": "datetime",
        "duration_minutes": "int"
    },

    "output": {
        "start_time": "time",
        "end_time": "time"
    },

    "prerequisites":
        """
        Requires free_slots from find_free_slots.
        Requires duration_minutes.
        Requires a valid date.
        """,

    "next_possible_tools": [
        "schedule_task",
        "update_event"
    ],

    "example_output": {
        "start_time": "09:00",
        "end_time": "12:00"
    }
}
,
"schedule_task_auto": {
    "function": schedule_task_auto_tool,

    "description":
        """
        Create a calendar event using an already
        selected start and end datetime.
        This tool does not search for free slots.
        This tool only creates the event.
        """,

    "use_when":
        """
        Use when:
        - A valid slot has already been selected.
        - An event needs to be created.
        - Scheduling logic has already been completed.
        """,

    "prerequisites": [
        "choose_best_slot"
    ],

    "input_parameters": {
        "title": "str",
        "start_datetime": "datetime",
        "end_datetime": "datetime"
    },

    "output": {
        "event_id": "str",
        "title": "str",
        "start_datetime": "datetime",
        "end_datetime": "datetime",
        "status": "created"
    },

    "example_output": {
        "event_id": "abc123",
        "title": "Team Sync",
        "start_datetime": "2026-12-25T09:00:00",
        "end_datetime": "2026-12-25T12:00:00",
        "status": "created"
    }
},
"schedule_task_fixed_time": {
    "function": schedule_task_fixed_tool,

    "description":
        """
        Create a calendar event at a specific
        user-provided date and time.

        This tool does not search for availability.
        This tool assumes the user has already
        chosen the exact start time.
        """,

    "use_when":
        """
        Use when:
        - User provides an exact date and time.
        - User says:
            'Schedule Team Sync tomorrow at 3 PM'
            'Create a meeting on Friday at 10 AM'
            'Book a call at 2 PM'

        Do not use when:
        - The user asks for any available slot.
        - The user wants automatic scheduling.
        - A free slot must first be found.
        """,

    "prerequisites": [],

    "input_parameters": {
        "title": "str",
        "start_datetime": "datetime",
        "duration_minutes": "int"
    },

    "output": {
        "event_id": "str",
        "title": "str",
        "start_datetime": "datetime",
        "end_datetime": "datetime",
        "status": "created"
    },

    "example_output": {
        "event_id": "abc123",
        "title": "Team Sync",
        "start_datetime": "2026-12-25T15:00:00",
        "end_datetime": "2026-12-25T18:00:00",
        "status": "created"
    }
},

"find_next_available_day": {
    "function": next_available_day_tool,

    "description":
        """
        Find the earliest future day that contains
        a free slot large enough to accommodate
        the requested duration.
        """,

    "use_when":
        """
        Use when:
        - User wants the next available day.
        - User says 'sometime next week'.
        - User says 'within the next few days'.
        - User wants the earliest available slot.
        - Automatic scheduling or rescheduling is required.
        """,

    "prerequisite_tools": [],

    "input_parameters": {
        "start_date": "datetime",
        "duration_minutes": "int",
        "max_days": "int"
    },

    "output": {
        "date": "date",
        "slot": {
            "start_time": "time",
            "end_time": "time"
        }
    },

    "example_output": {
        "date": "2026-09-10",
        "slot": {
            "start_time": "10:00",
            "end_time": "11:30"
        }
    }
},
"reschedule_task_fixed": {
    "function": reschedule_task_fixed_tool,

    "description":
        "Move an existing event to an exact date and time.",

    "prerequisite_tools": [
        "find_event_by_title"
    ],

    "input_parameters": {
        "event_id": "str",
        "title": "str",
        "start_datetime": "datetime",
        "end_datetime": "datetime"
    },

    "output": {
        "updated_event": "calendar_event"
    }
},
"reschedule_task_day": {
    "function": reschedule_task_day_tool,

    "description":
        """
        Move an event to a specific day using a slot
        selected by previous workflow steps.
        """,

    "prerequisite_tools": [
        "find_event_by_title",
        "find_free_slots",
        "choose_best_slot"
    ],

    "input_parameters": {
        "event_id": "str",
        "title": "str",
        "start_datetime": "datetime",
        "end_datetime": "datetime"
    },

    "output": {
        "updated_event": "calendar_event"
    }
},
"reschedule_task_next_available": {
    "function": reschedule_task_next_available_tool,

    "description":
    """
    Move an existing event to the earliest available
    free slot found within the specified date range.
    """,

    "prerequisite_tools": [
        "find_event_by_title",
        "find_next_available_day"
    ],

    "input_parameters": {
        "event_id": "str",
        "title": "str",
        "start_datetime": "datetime",
        "end_datetime": "datetime"
    },

    "output": {
        "updated_event": "calendar_event"
    }
},

"delete_task": {
    "function": delete_task_tool,

    "description":
        """
        Delete an existing calendar event.
        """,

    "use_when":
        """
        User wants to remove, cancel,
        or delete an event.
        """,

    "prerequisite_tools": [
        "find_event_by_title"
    ],

    "input_parameters": {
        "event_id": "str"
    },

    "output": {
        "success": "bool",
        "message": "str"
    }
}
    
}

def get_tool_descriptions():

    descriptions = []

    for name, info in TOOLS.items():

        descriptions.append(
            f"""
Tool: {name}

Description:
{info.get('description', '')}

Use When:
{info.get('use_when', '')}

Prerequisite Tools:
{info.get('prerequisite_tools', [])}

Input Parameters:
{info.get('input_parameters', {})}

Output:
{info.get('output', {})}
"""
        )

    return "\n".join(descriptions)