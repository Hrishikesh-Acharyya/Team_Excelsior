
from django import forms
from .models import AppointmentModel

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = AppointmentModel
        fields = [
            'doctor', 'appointment_time', 'symptoms',
            'full_name', 'phone_number', 'email',
            'age', 'gender', 'prefferedLanguage'
        ]
        widgets = {
            'appointment_time': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }
