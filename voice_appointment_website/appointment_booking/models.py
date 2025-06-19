from django.db import models
from django.conf import settings
from doctor.models import DoctorModel  # Make sure Doctor is defined in this or another module


"""
Appointment model for storing appointment details.
Not creating a separate model for Patient due to time constraints
and the assumption that patient info can be derived from the LLM structure data or User model.
Linked with Doctor model so the doctor dashboard if created can utilise this model to show appointments.
"""
class AppointmentModel(models.Model):
    doctor = models.ForeignKey(DoctorModel, on_delete=models.SET_NULL)
    appointment_time = models.DateTimeField()

    # Patient Info (from LLM structure data or User)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=12)
    email = models.EmailField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        null=True, blank=True
    )

    # Medical Info
    symptoms = models.TextField()
    prefferedLanguage = models.CharField(max_length=30, null=True, blank=True)

    # Logged-in user (optional link)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.CASCADE, related_name='booked_appointments'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    #appointment status
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='scheduled'
    )

    def __str__(self):
        return f"{self.full_name} - {self.doctor.name} @ {self.appointment_time}"

# Create your models here.
