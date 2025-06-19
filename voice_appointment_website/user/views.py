from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer
from django.views import View
from django.contrib import messages

class registerUser(APIView):
    
    """
    API View to handle user registration.
    """
    def post(self,request):
      serializer = UserRegistrationSerializer(data=request.data)
      if serializer.is_valid(): #validates the data
          serializer.save() #saves the user data to the database
          return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
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

class loginUser:
    # Placeholder for the login user view
    pass

# Create your views here.
