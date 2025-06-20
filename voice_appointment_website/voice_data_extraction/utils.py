from datetime import datetime, timedelta
from doctor.models import DoctorModel
from appointment_booking.utils import get_available_slots
import dateparser  # pip install dateparser


"""
Takes the structured output from the LLM and finds the nearest available appointment slot for a doctor.
"""
def find_nearest_available_slot(llm_output):
    #Identify doctor (by name or specialization)
    doctor = None
    if llm_output.get("doctor"):
        doctor = DoctorModel.objects.filter(name__icontains=llm_output["doctor"]).first()
    elif llm_output.get("specialization"):
        doctor = DoctorModel.objects.filter(specialization__icontains=llm_output["specialization"]).first()
    else:
        # fallback to General Medicine if no specialization provided
        doctor = DoctorModel.objects.filter(specialization__icontains="General Medicine").first()

    if not doctor:
        return {"error": "No matching doctor found"}

   # Parse preferred time
    preferred_str = llm_output.get("datetime")
    if not preferred_str:
        preferred_str = datetime.now().isoformat()
    preferred_dt = dateparser.parse(str(preferred_str))
    now = datetime.now()
    # Ensure preferred_dt is not in the past or parsing failed
    if not preferred_dt or preferred_dt < now:
        preferred_dt = now + timedelta(minutes=30)

    # Always start searching from the later of preferred_dt.date() and today
    search_start_date = max(preferred_dt.date(), now.date())
    print(preferred_dt, search_start_date)

    # Generate available slots for next 7 days
    for offset in range(7):
        target_date = search_start_date + timedelta(days=offset)
        available_slots = get_available_slots(doctor, target_date)

        # On the first day, only consider slots after preferred_dt
        for slot in available_slots:
            if (target_date == preferred_dt.date() and slot >= preferred_dt) or (target_date > preferred_dt.date()):
                return {
                    "doctor": doctor.name,
                    "slot": slot.strftime("%Y-%m-%d %H:%M"),
                    "specialization": doctor.specialization
                }

    return {"error": "No available slots in the next 7 days"}
