from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer
from django.views import View
from django.contrib import messages
from django.contrib.auth import login, logout
from .models import User  
import random
from twilio.rest import Client  
from django.conf import settings
from dotenv import load_dotenv
import os

load_dotenv()

class registerUser(APIView):
    
    """
    API View to handle user registration.
    """
    def post(self,request):
      serializer = UserRegistrationSerializer(data=request.data)
      if serializer.is_valid(): #validates the data
          serializer.save() #saves the user data to the database
          messages.success(request, "User registered successfully")
          return Response( status=status.HTTP_201_CREATED)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  #contains all fieldlevel, modellevel, serializerlevel validator errors
  
class registerUserForm(View):
    
    """
    View to render the user registration form and handle form submission.
    """

    """
    Handles GET request to render the registration form.
    """
    def get(self, request):
        return render(request, 'register.html')
    
    """
    Handles POST request to process the registration form submission.
    Uses same serializer as the API view to validate and save user data.
    Displays success or error messages based on the validation results.
    """

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.POST)

        try:
          if serializer.is_valid():
              serializer.save()
              messages.success(request, "User registered successfully")
              return render(request, 'index.html', {"message": "User registered successfully."})
          
          for field, errors in serializer.errors.items():
              for error in errors:
                  messages.error(request, f"{field}: {error}")
        except Exception as e:
          messages.error(request, str(e))
        return render(request, 'register.html')

def loginUser(request):
    # Consume all previous messages so none are shown on this page
    list(messages.get_messages(request))
    if request.method == "GET":
        return render(request, "login.html")
    # Add POST logic here 
    return request_otp_view(request)  # Always return a response

def sendOTPSMS(phone_number, otp):

    client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
    message = client.messages.create(
        body=f"Your OTP for login is: {otp}",
        from_=os.getenv('TWILIO_PHONE_NUMBER'),  # Your Twilio phone number
        to=f"+91{phone_number}"
    )
    return message.sid  # Return the message SID for logging or tracking purposes

def request_otp_view(request):
    
    """
    Works when the user requests an OTP for login.
    It checks if the user exists with the provided phone number and full name for extra authentication
    and generates a 6-digit OTP for that user.
    The OTP is then sent to the user's phone number via SMS (simulated here with a print statement).
    If the user is not found, an error message is displayed.
    """
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        full_name = request.POST.get('full_name')
        try:
            user = User.objects.get(phone_number=phone_number, full_name=full_name)
        except User.DoesNotExist:
            messages.error(request, 'User not found')
            return render(request, 'login.html')

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.save()

        # Here you would send the OTP via SMS to the user's phone number
        print(f"OTP for {phone_number} is {otp}")  # replace with SMS later
        sendOTPSMS(phone_number, otp)


        return render(request, 'otp.html', {'phone_number': phone_number})

    return render(request, 'login.html')


def verify_otp_view(request):
    if request.method == 'POST':
        otp = request.POST.get('otp', '').strip()
        phone_number = request.POST.get('phone_number')
        try:
            user = User.objects.get(phone_number=phone_number, otp=otp)
        except User.DoesNotExist:
            messages.error(request, 'Invalid OTP or phone number')
            return render(request, 'otp.html', {'phone_number': phone_number})

        user.otp = None  # clear OTP after successful login
        user.save()
        login(request, user)  # Django session login
        return redirect('index')  # Or wherever you want

    return render(request, 'login.html')


def logout_view(request):
    
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('index')  # or wherever you want to redirect after logout
