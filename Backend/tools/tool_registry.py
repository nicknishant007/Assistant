from tools.calendar_tool import (
    get_events_tool,
    find_event_by_title_tool
)

from tools.scheduler_tool import (
    schedule_task_fixed_tool,
    schedule_task_auto_tool,
    reschedule_event_tool,
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
        Search calendar events using a title and return
        the most relevant matching event together with
        alternative matches.

        This tool is the primary event lookup tool.

        It returns normalized event information including:

        - event_id
        - title
        - date
        - day
        - start_datetime
        - end_datetime
        - start_time
        - end_time
        - duration_minutes

        Use this tool whenever later workflow steps
        require information about an existing event.

        The returned event data should be reused instead
        of manually reconstructing event information.
        """,

    "use_when":
        """
        Use when:

        - User mentions an event name.
        - User wants to update an event.
        - User wants to reschedule an event.
        - User wants to delete an event.
        - User refers to:
            'that meeting'
            'that event'
            'move it'
            'delete it'
            'reschedule it'

        - Event duration is needed.
        - Event date is needed.
        - Event start/end time is needed.
        - Event start/end datetime is needed.
        - Event metadata is required for later workflow steps.
        """,

    "prerequisite_tools": [],

    "input_parameters": {

        "title": "str",
        "date": "str (optional, ISO date)",
        "day":"str (optional, monday-sunday)"
    },

    "output": {

        "found": "bool",

        "best_match": {

            "event_id": "str",
            "title": "str",
            "date": "date",
            "day": "str",
            "start_datetime": "datetime",
            "end_datetime": "datetime",
            "start_time": "time",
            "end_time": "time",
            "duration_minutes": "int",
            "score": "float"
        },

        "alternatives": [
            {

                "event_id": "str",
                "title": "str",
                "date": "date",
                "day": "str",
                "start_datetime": "datetime",
                "end_datetime": "datetime",
                "start_time": "time",
                "end_time": "time",
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
            "date": "2026-09-10",
            "day": "thursday",
            "start_datetime": "2026-09-10T10:00:00+05:30",
            "end_datetime":"2026-09-10T11:00:00+05:30",
            "start_time": "10:00",
            "end_time": "11:00",
            "duration_minutes": 60,
            "score": 100
        },

        "alternatives": [
            {

                "event_id": "xyz456",
                "title": "Team Sync Weekly",
                "date": "2026-09-12",
                "day": "saturday",
                "start_datetime":"2026-09-12T14:00:00+05:30",
                "end_datetime":"2026-09-12T15:00:00+05:30",
                "start_time": "14:00",
                "end_time": "15:00",
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
        "end_time": "time",

        "start_datetime": "datetime",
        "end_datetime": "datetime"
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
        "end_time": "10:00",

        "start_datetime":
            "2026-09-20T09:00:00",

        "end_datetime":
            "2026-09-20T10:00:00"
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
        You have to find a free slot first using find_free_slots
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
        Find the earliest future day containing a free slot
        large enough for the requested duration.

        Returns the selected slot including complete
        start_datetime and end_datetime values.

        Use these datetime values directly in scheduling
        or rescheduling tools.

        Do not manually construct datetime strings.
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
            "end_time": "time",

            "start_datetime": "datetime",
            "end_datetime": "datetime"
        }
    },

    "example_output": {
        "date": "2026-09-10",

        "slot": {
            "start_time": "10:00",
            "end_time": "11:30",

            "start_datetime": "2026-09-10T10:00:00+05:30",
            "end_datetime": "2026-09-10T11:30:00+05:30"
        }
    }
},
"reschedule_event": {

    "function": reschedule_event_tool,

    "description":
        """
        Reschedule an existing calendar event.

        This is the primary tool for all event
        rescheduling operations.

        The tool updates an existing event's
        schedule while preserving all event
        information that is not explicitly changed.

        Supports:

        - Moving an event to a new date.
        - Moving an event to a new time.
        - Moving an event to a new date and time.
        - Moving an event while preserving the
          original time.
        - Moving an event while preserving the
          original duration.
        - Moving an event to a selected free slot.
        - Moving an event to the next available slot.
        - Rescheduling using exact datetime values.
        - Rescheduling using date + start_time + end_time.

        This tool only performs the final event update.

        Any required scheduling information should be
        obtained by previous workflow steps or provided
        directly by the user.
        """,

    "use_when":
        """
        Use when:

        - User wants to reschedule an event.
        - User wants to move an event.
        - User wants to postpone an event.
        - User wants to shift an event.
        - User wants to change an event date.
        - User wants to change an event time.
        - User wants to move an event to another day.
        - User wants to move an event to another time.
        - User says:
            * move event
            * reschedule event
            * postpone event
            * shift event
            * move to another day
            * move to another time
            * same time
            * keep timing
            * same schedule
            * preserve duration
            * next available slot

        Required inputs:

        - event_id
        - title

        Scheduling information may come from:

        - user supplied datetime values
        - find_free_slots
        - choose_best_slot
        - find_next_available_day
        - previous workflow steps

        This tool should be the final step of every
        rescheduling workflow.
        """,

    "prerequisite_tools": [],

    "input_parameters": {

        "event_id": "str",

        "title": "str",

        "start_datetime":
            "ISO-8601 datetime (optional)",

        "end_datetime":
            "ISO-8601 datetime (optional)",

        "date":
            "YYYY-MM-DD (optional)",

        "start_time":
            "HH:MM:SS (optional)",

        "end_time":
            "HH:MM:SS (optional)"
    },

    "output": {
        "updated_event": "calendar_event"
    },

    "example_output": {

        "updated_event": {

            "event_id": "abc123",

            "title": "Team Sync",

            "start_datetime":
                "2026-09-27T10:00:00+05:30",

            "end_datetime":
                "2026-09-27T11:00:00+05:30"
        }
    }
,

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