1. Will be using whisper to take audio from frontend and process it in the backend. Whisper Ai has better language detection ability and more language support and better features
2. Will be using llama together.ai to structure data
3. Using django framwework for backend
4. Using django rest framework to manage API calls
5. Using postgreSQL for database
   
##  To run code in your environment, in the terminal, run 'python install -r requirements.txt'.  check the .env.example file, copy it and paste values according to your system. Implemented the ai and voice to text. No multilingual support yet. Yet to create database models


** model flow-> User may or may not login. If logged in, the data will be taken from profile itself. User will just have to specify the doctor name, speciality, and data and symptoms. Then an appointment model will be created. Here all the patient data along with appointment data will be stored. Can have otp based login system so no password needed. emaqil will be sent to user for confiration as well as whatsapp. The booking can be managed from there. The appointment will be linked to the user and doctor if loggedin . If not logged in it will be liniked to the doctor to extract time and date. do not give code yet.
1. Specialty Should Be Tied to Doctor Model, Not Input
Let users say e.g. “I want to see a dermatologist” — but you should:

Match the specialization to a doctor

Don’t store specialization again in Appointment, it's part of the Doctor

➡️ Instead: Use specialization input to lookup doctors and store only the doctor in the appointment.

2. Avoid Duplicate Users If They Reuse Email
If a guest books an appointment with an email that already exists:

Either auto-link the appointment to the existing user

Or create a temporary user and merge later (if they sign up)

➡️ Solution: Use email as a unique identity anchor even for anonymous users.

3. Consider a GuestToken model
If users aren’t logged in, but need to:

Check status

Cancel/change appointment

➡️ Generate a unique token per appointment and send it via email/WhatsApp. You can store it as a field in the model (appointment_token = models.CharField(...)).

This allows secure lookup without needing full login.

4. Add is_confirmed, is_completed, is_cancelled to Appointment
This makes it easier to manage appointment state later in admin panel or user dashboard.

5. Doctor's Availability Should Be in Separate Model
Instead of available_slots = JSONField(...), define:

no slot overlapping. give 10 - 10 min slots fixed

✅ Yes: The Appointment model should be linked to the PatientProfile model — not directly to the User model — because:
A single user (e.g. father) can book for multiple patients (e.g. son, daughter, self)

The patient's medical info (age, gender, name) is stored in the PatientProfile

This avoids duplication and keeps the data clean and normalized

✅ Clean Relationship:
scss
Copy
Edit
User (e.g. Father) ──┬─────────────▶ PatientProfile (e.g. Son)
                    └─────────────▶ PatientProfile (e.g. Self)
                                       │
                                       ▼
                               Appointment
✅ So your Appointment model should look like this:
python
Copy
Edit
class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    appointment_datetime = models.DateTimeField()
    symptoms = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment for {self.patient.full_name} with {self.doctor.name}"
✅ Why This Is Good:
Field	Source
patient.full_name	From PatientProfile
patient.age, gender, relation	From PatientProfile
user.phone_number	From the parent User
doctor.availability	From the Doctor model

So everything stays nicely separated and connected.

✅ Optional: If You Still Want a Link to User
You can still include the user who booked it:

python
Copy
Edit
user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
This way:

You know who booked the appointment

You still keep patient data separate

Works even if the patient is different from the user

Let me know if you'd like help defining the full PatientProfile, Appointment, and Doctor models together — or if you're ready to move on to serializers and views.