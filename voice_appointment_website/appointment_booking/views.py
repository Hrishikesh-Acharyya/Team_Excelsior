from django.shortcuts import render
from django.conf import settings
from django.urls import reverse_lazy
from datetime import timedelta
from datetime import datetime
from django.contrib import messages
from .models import AppointmentModel
from .forms import AppointmentForm
from django.views.generic.edit import FormView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from doctor.models import DoctorModel
from appointment_booking.utils import generate_time_slots
from django.contrib.auth import get_user_model


def index(request):
    """
    Render the index page for the appointment booking application.
    """
    return render(request, 'index.html')

def book_appointment(request):
    """
    Render the appointment booking page.
    """
    doctors = DoctorModel.objects.all()
    return render(request, 'appointment.html', {'doctors': doctors, 'HOST_NAME': settings.HOST_NAME})

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

User = get_user_model()

class CreateAppointmentView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        try:
            data = request.data
            doctor_id = data.get('doctorId')
            date_str = data.get('date')  # YYYY-MM-DD
            time_str = data.get('time')  # HH:MM

            if not all([doctor_id, date_str, time_str]):
                return Response({'error': 'Missing required fields'}, status=400)

            try:
                doctor = DoctorModel.objects.get(id=doctor_id)
            except DoctorModel.DoesNotExist:
                return Response({'error': 'Doctor not found'}, status=404)

            appointment_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

            appointment = AppointmentModel.objects.create(
                user=request.user if request.user.is_authenticated else None,
                doctor=doctor,
                appointment_time=appointment_time,
                full_name=data.get('name'),
                age=data.get('age'),
                gender=data.get('gender'),
                phone_number=data.get('phone'),
                email=data.get('email'),
                symptoms=data.get('symptoms'),
            )

            return Response({'success': 'Appointment created successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)