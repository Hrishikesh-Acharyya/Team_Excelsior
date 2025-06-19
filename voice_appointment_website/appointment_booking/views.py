from django.shortcuts import render
from django.conf import settings
from django.urls import reverse_lazy
from datetime import timedelta
from django.contrib import messages
from .models import AppointmentModel
from .forms import AppointmentForm
from django.views.generic.edit import FormView


def index(request):
    """
    Render the index page for the appointment booking application.
    """
    return render(request, 'index.html')

def book_appointment(request):
    """
    Render the appointment booking page.
    """
    return render(request, 'appointment.html', {'HOST_NAME': settings.HOST_NAME})

class AppointmentCreateView(FormView):
    """
    View to handle the creation of a new appointment.
    """

    template_name = 'appointment.html'  
    form_class = AppointmentForm
    success_url = reverse_lazy('success')  #success URL after appointment creation
    
    def form_valid(self, form):
        appointment_time = form.cleaned_data['appointment_time']
        doctor = form.cleaned_data['doctor']

        # Slot conflict check (±15 mins)
        slot_start = appointment_time - timedelta(minutes=15)
        slot_end = appointment_time + timedelta(minutes=15)
        conflict = AppointmentModel.objects.filter(
            doctor=doctor,
            appointment_time__range=(slot_start, slot_end)
        ).exists()

        if conflict:
            form.add_error('appointment_time', 'This time slot is already booked.')
            return self.form_invalid(form)

        # If logged in, override patient fields from user
        if self.request.user.is_authenticated:
            form.instance.full_name = self.request.user.full_name
            form.instance.phone_number = self.request.user.phone_number
            form.instance.email = self.request.user.email
            form.instance.user = self.request.user

        # Save the appointment
        form.save()
        messages.success(self.request, "✅ Appointment booked successfully!")
        return super().form_valid(form)
