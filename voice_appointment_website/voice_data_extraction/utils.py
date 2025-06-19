from datetime import datetime, timedelta
from doctor.models import Doctor
from appointment_booking.utils import get_available_slots
import dateparser  # pip install dateparser


"""
Takes the structured output from the LLM and finds the nearest available appointment slot for a doctor.
"""
def find_nearest_available_slot(llm_output):
    #Identify doctor (by name or specialization)
    doctor = None
    if llm_output.get("doctor_name"):
        doctor = Doctor.objects.filter(name__icontains=llm_output["doctor_name"]).first()
    elif llm_output.get("specialization"):
        doctor = Doctor.objects.filter(specialization__icontains=llm_output["specialization"]).first()
    
    if not doctor:
        return {"error": "No matching doctor found"}

   # Parse preferred time
    preferred_str = llm_output.get("preferred_time", "")
    preferred_dt = dateparser.parse(preferred_str) or datetime.now()

    # Generate available slots for next 7 days
    for offset in range(7):  # Look 7 days ahead
        target_date = (preferred_dt.date() + timedelta(days=offset))
        available_slots = get_available_slots(doctor, target_date)
        
       # Find the nearest available slot after preferred time
        for slot in available_slots:
            if slot >= preferred_dt:
                return {
                    "doctor": doctor.name,
                    "slot": slot.strftime("%Y-%m-%d %H:%M"),
                    "specialization": doctor.specialization
                }
    
    return {"error": "No available slots in the next 7 days"}
