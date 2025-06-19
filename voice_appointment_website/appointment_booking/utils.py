from datetime import datetime, timedelta, time

#TODO: better handling of vague time inputs

def generate_time_slots(doctor, slot_minutes=15, date=None):
    """
    Generate all time slots between doctor's working hours on a given date.
    Returns a list of datetime objects.
    """
    slots = []
    # Combine date with time if needed
    if date is None:
        date = datetime.today().date()
    day_start = datetime.combine(date, doctor.start_hour)
    lunch_start = datetime.combine(date, doctor.lunch_start)
    lunch_end = datetime.combine(date, doctor.lunch_end)
    evening_break_start = datetime.combine(date, doctor.evening_break_start)
    evening_break_end = datetime.combine(date, doctor.evening_break_end)
    day_end = datetime.combine(date, doctor.end_hour)

    # Morning slots before lunch
    current_time = day_start
    while current_time + timedelta(minutes=slot_minutes) <= lunch_start:
        slots.append(current_time)
        current_time += timedelta(minutes=slot_minutes)

    # Afternoon slots after lunch
    current_time = lunch_end
    while current_time + timedelta(minutes=slot_minutes) <= evening_break_start:
        slots.append(current_time)
        current_time += timedelta(minutes=slot_minutes)

    # Evening slots after evening break
    current_time = evening_break_end
    while current_time + timedelta(minutes=slot_minutes) <= day_end:
        slots.append(current_time)
        current_time += timedelta(minutes=slot_minutes)

    return slots

def get_available_slots(doctor, date, slot_minutes=15):
    """
    Get available time slots for a doctor on a given date.
    Returns a list of datetime objects.
    """
    all_slots = generate_time_slots(doctor, slot_minutes, date)
    # all_slots are already datetime objects

    booked_slots = doctor.appointmentmodel_set.filter(
        appointment_time__date=date #django field lookup to filter by date. __date extracts the date part from datetime
    ).values_list('appointment_time', flat=True)
    booked_slots = set(booked_slots)
    available = [slot for slot in all_slots if slot not in booked_slots]

    return available










