import openai
import datetime
from gcsa.google_calendar import GoogleCalendar
import datetime
import json
from dateutil.parser import parse
from gcsa.event import Event
import pytz


CREDENTIALS_PATH = "credentials.json"
EMAIL = "johnrobgillis@gmail.com"

current_date = datetime.datetime.now().date().strftime('%Y-%m-%d')  # Format as 'YYYY-MM-DD'
    
messages = [
        {"role": "system", "content": f"The current day is {current_date}"},
        {"role": "system", "content": "You are my personal executive assistnat"},
        {"role": "user", "content": "Before you schedule any calendar events use the fetch_google_calendar_events to make sure the time is slot is open"},
        {"role": "user", "content": "Hello you are my personal executive assistant! Let's get planning!"}
    ]

functions = [
    {
        "name": "fetch_google_calendar_events",
        "description": "Retrieves the list of events from the user's Google Calendar for a specified date range and optional query.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_time": {
                    "type": "string",
                    "description": "Start time for the range of events to fetch in ISO format, e.g. '2023-10-25T16:00:00'."
                },
                "end_time": {
                    "type": "string",
                    "description": "End time for the range of events to fetch in ISO format, e.g. '2023-10-25T16:00:00'."
                },
                "query": {
                    "type": "string",
                    "description": "Text used for searching the event's details."
                },
                "single_events": {
                    "type": "boolean",
                    "description": "Whether to return only single events or recurring events too."
                }
            },
            "required": ["start_time", "end_time"],
        }
    },
    {
        "name": "create_google_calendar_events",
        "description": "Create one or more events in Google Calendar from a string representation of events.",
        "parameters": {
            "type": "object",
            "properties": {
                "events_string": {
                    "type": "string",
                    "description": "A string representation of events. Each event is separated by ';' and each event detail is separated by ','. The order of details is: 'summary', 'start', 'end'. E.g., 'Meeting,2023-10-28T16:00:00,2023-10-28T18:00:00;Lunch,2023-10-29T12:00:00,2023-10-29T13:00:00'."
                }
            },
            "required": ["events_string"],
        }
    },
    {
        "name": "delete_google_calendar_events",
        "description": "Delete one or multiple events from the user's Google Calendar using the provided event_ids",
        "parameters": {
            "type": "object",
            "properties": {
                "event_ids": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "description": "List of event IDs to be deleted",
                },
            },
            "required": ["event_ids"],
        },
    }
    
]

def delete_google_calendar_events(event_ids) -> str:
    """
    Deletes one or multiple events from the user's Google Calendar using the provided event_ids.
    
    Args:
    - event_ids (list): List of event IDs to be deleted.
    
    Returns:
    - str: A message indicating the status of the deletion.
    """
    
    gc = GoogleCalendar(EMAIL, credentials_path=CREDENTIALS_PATH)
    errors = []
    
    # Ensure event_ids is a list
    if not isinstance(event_ids, list):
        event_ids = [event_ids]

    for event_id in event_ids:
        try:
            gc.delete_event(event_id)
        except Exception as e:
            errors.append(f"Error deleting event with ID {event_id}: {str(e)}")

    if errors:
        return "\n".join(errors)
    else:
        return f"All events have been successfully deleted."



# def check_events_and_schedule(start_time_str, end_time_str, event_details_str):
#     """
#     Checks for any existing events in the given time range. 
#     If there are no events, it schedules the given event. 
#     If there are events, it returns the overlapping events.
    
#     Args:
#     - start_time_str (str): Start time for the range in ISO format.
#     - end_time_str (str): End time for the range in ISO format.
#     - event_details_str (str): A string representation of the event to schedule if free.
#         The format is: 'summary,start,end' 
    
#     Returns:
#     - dict: Contains either details of the created event or details of overlapping events.
#     """
    
#     # Fetch existing events from Google Calendar for the given range
#     existing_events = fetch_google_calendar_events(start_time_str, end_time_str)
    
#     # Debug: Print fetched events
#     print(f"Fetched events between {start_time_str} and {end_time_str}:")
#     for event in existing_events:
#         print(event)
    
#     # Parse the desired event's details
#     summary, desired_start_str, desired_end_str = event_details_str.split(',')
#     desired_start = parse(desired_start_str)
#     desired_end = parse(desired_end_str)

#     # Adjust desired event timings based on timezone of the existing events
#     if existing_events:
#         event_timezone = parse(existing_events[0]["start"]).tzinfo
#         desired_start = desired_start.astimezone(event_timezone)
#         desired_end = desired_end.astimezone(event_timezone)

#     # Debug: Print the adjusted desired event timings
#     print(f"Adjusted desired event timings: Start = {desired_start}, End = {desired_end}")

#     overlapping_events = []
#     for event in existing_events:
#         event_start = parse(event["start"])
#         event_end = parse(event["end"])
        
#         # Check for overlaps
#         if (event_start < desired_end) and (event_end > desired_start):
#             overlapping_events.append(event)
            
#     # Debug: Print overlapping events, if any
#     if overlapping_events:
#         print("Found overlapping events:")
#         for event in overlapping_events:
#             print(event)
#     else:
#         print("No overlapping events found.")

#     # If there are no overlaps, schedule the new event
#     if not overlapping_events:
#         created_event = create_google_calendar_events(event_details_str)
#         return {
#             "status": "success",
#             "message": "Event scheduled successfully.",
#             "events": format_created_events_for_display(created_event)
#         }
    
#     # If there are overlaps, return them
#     else:
#         return {
#             "status": "overlap",
#             "message": "There are overlapping events during the specified period.",
#             "events": overlapping_events
#         }

def create_google_calendar_events(events_string: str):
    """
    Create one or more events in Google Calendar.
    
    Args:
    - events_string (str): A string representation of events. Each event is separated by ';'
        and each event detail is separated by ','. The order of details is:
            'summary', 'start', 'end'
            
    Returns:
    - list[Event]: A list of created Event objects.
    """

    gc = GoogleCalendar(EMAIL, credentials_path=CREDENTIALS_PATH)
    created_events = []

    # Split the string into individual events
    events = events_string.split(';')
    for event_str in events:
        event_parts = event_str.split(',')
        
        if len(event_parts) < 3:
            raise ValueError("Each event string must have at least summary, start, and end details.")
        
        summary = event_parts[0]
        start_str = event_parts[1]
        end_str = event_parts[2]
        
        # Convert string representation to date/datetime objects
        start = parse(start_str)
        end = parse(end_str)

        # Create the event
        event = Event(summary, start=start, end=end)
        created_event = gc.add_event(event)
        created_events.append(created_event)
        
    return created_events

def format_created_events_for_display(events):
    """
    Formats the created events for display.
    
    Args:
    - events (list[Event]): List of created Event objects.

    Returns:
    - str: Formatted string for display.
    """
    formatted_events = []
    for event in events:
        event_str = f"Event '{event.summary}' created from {event.start} to {event.end}."
        formatted_events.append(event_str)

    return "\n".join(formatted_events)


def fetch_google_calendar_events(start_time, end_time, query=None, single_events=False) -> list:
    """
    Retrieves the list of events from the user's Google Calendar for a specified date range and optional query.
    
    This function connects to the Google Calendar associated with the provided email
    and fetches the list of events scheduled. It can be used to:
    - Check availability on a particular date/time.
    - Find out the next upcoming event.
    - Review daily or weekly schedules.
    - Avoid overlapping or double-booking events.
    - Search for events based on a specific query.
    
    Args:
    - start_time (date or datetime): Start time for the range of events to fetch.
    - end_time (date or datetime): End time for the range of events to fetch.
    - query (str, optional): Text used for searching the event's details.
    
    Returns:
    - list: A list of events from the Google Calendar.
    """
    
    # Convert string representations of datetimes into actual datetime objects
    start_time = parse(start_time)
    end_time = parse(end_time)
    
    gc = GoogleCalendar(EMAIL, credentials_path=CREDENTIALS_PATH)
    
    # Fetch events
    events = list(gc.get_events(time_min=start_time, time_max=end_time, query=query, single_events=single_events))
    
    # Convert events to your desired format
    events_list = [
        {
            "event_id": event.event_id,
            "summary": event.summary, 
            "start": str(event.start), 
            "end": str(event.end), 
            "description": event.description
        } 
        for event in events
    ]
    
    return events_list


def format_events_for_display(events: list) -> str:
    """Format the events list into a readable string for display."""
    if not events:
        return "No events found in your Google Calendar."
    
    event_strings = []
    for event in events:
        event_str = f"ID: {event['event_id']} | {event['start']} - {event['end']}: {event['summary']} | Description: {event['description']}"
        event_strings.append(event_str)
    
    return "\n".join(event_strings)


def run_conversation():

    while True:
        print('Starting conversation......')
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
            functions=functions,
            function_call="auto",
        )
        print("RESPONSE\n--------")
        print(response)
        print("------")
        response_message = response["choices"][0]["message"]
        print("Assistant:", response_message["content"])
        messages.append(response_message)  # Add the assistant's response to the conversation

        if response_message.get("function_call"):
            available_functions = {
                "fetch_google_calendar_events": fetch_google_calendar_events,
                "create_google_calendar_events": create_google_calendar_events,
                "delete_google_calendar_events": delete_google_calendar_events,
                
            }

            function_name = response_message["function_call"]["name"]
            function_to_call = available_functions.get(function_name)
            if not function_to_call:
                raise ValueError(f"The function '{function_name}' is not recognized.")

            function_args_str = response_message["function_call"]["arguments"]
            function_args = json.loads(function_args_str)
            function_response = function_to_call(**function_args)

            if function_name == "fetch_google_calendar_events":
                formatted_response = format_events_for_display(function_response)
            elif function_name == "create_google_calendar_events":
                formatted_response = format_created_events_for_display(function_response)
            elif function_name == "delete_google_calendar_events":
                formatted_response = function_response
            else:
                formatted_response = str(function_response)  # Generic response for any other function


            messages.append({
                "role": "function",
                "name": function_name,
                "content": formatted_response,
            })

            # Get a new response from GPT where it can see the function response
            second_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                messages=messages,
            )
            second_response_message = second_response["choices"][0]["message"]
            print("Assistant:", second_response_message["content"])
            messages.append(second_response_message)  # Add the assistant's second response to the conversation

        user_input = input("You: ")
        if user_input.lower() == "end":
            break
        messages.append({
            "role": "user",
            "content": user_input
        })

run_conversation()




#
#print(run_conversation())
