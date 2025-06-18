from django.shortcuts import render
from django.conf import settings


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
# Create your views here.
