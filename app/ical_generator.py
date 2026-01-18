"""iCalendar generation utilities."""

from datetime import datetime, timedelta
import uuid

from icalendar import Calendar, Event


DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
HOURS = list(range(0, 24))
SLOT_DURATION_MINUTES = 15


def generate_ical(selections: dict, space_name: str = "Space") -> str:
    """
    Generate iCalendar string from selections.
    
    Args:
        selections: dict with format {"Monday": [{"hour": 9, "minute": 0}, ...], ...}
        space_name: Name of the space being scheduled
    
    Returns:
        iCalendar formatted string (RFC 5545)
    """
    cal = Calendar()
    cal.add('prodid', '-//Space Occupancy Scheduler//Demo//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', f'{space_name} Occupancy Schedule')
    
    # Get the start of the current week (Monday)
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    
    for day_name, slots in selections.items():
        if not slots:
            continue
            
        day_index = DAYS.index(day_name)
        event_date = monday + timedelta(days=day_index)
        
        # Convert slots to minutes from midnight for easier grouping
        minutes_list = sorted([s['hour'] * 60 + s['minute'] for s in slots])
        groups = _group_consecutive_slots(minutes_list)
        
        # Create an event for each group of consecutive slots
        for group in groups:
            start_minutes = group[0]
            end_minutes = group[-1] + SLOT_DURATION_MINUTES
            
            start_time = event_date + timedelta(minutes=start_minutes)
            end_time = event_date + timedelta(minutes=end_minutes)
            
            event = Event()
            event.add('summary', f'{space_name} - Occupied')
            event.add('dtstart', start_time)
            event.add('dtend', end_time)
            event.add('dtstamp', datetime.now())
            event['uid'] = f'{uuid.uuid4()}@space-scheduler'
            event.add('description', 'Space is occupied during this time block')
            cal.add_component(event)
    
    return cal.to_ical().decode('utf-8')


def _group_consecutive_slots(minutes_list: list[int]) -> list[list[int]]:
    """Group consecutive 15-minute slots into lists."""
    if not minutes_list:
        return []
    
    groups = []
    current_group = [minutes_list[0]]
    
    for minutes in minutes_list[1:]:
        if minutes == current_group[-1] + SLOT_DURATION_MINUTES:
            current_group.append(minutes)
        else:
            groups.append(current_group)
            current_group = [minutes]
    
    groups.append(current_group)
    return groups