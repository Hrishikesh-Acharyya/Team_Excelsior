from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re

class CustomUserManager(BaseUserManager):

  def validate_phone_number(self, phone_number):
    """
    Validates the phone number format.

    Regex pattern explanation: 
    ^ - start of string
    \+91[\-\s]? - optional country code +91 followed by an optional hyphen or space
    \[6-9] - first digit must be between 6 and 9 - This is true for indian phone numbers. Rule set by dept of Telecommunications,GOI
    \d{9} - followed by 9 digits (total 10 digits)
    $ - end of string
    """
    pattern = r'^(\+91[\-\s]?)?[6-9]\d{9}$'
    if not re.match(pattern, phone_number):
        raise ValidationError("Invalid phone number format. It should be a 10-digit Indian mobile number, optionally prefixed with +91.")

  def create_user(self, phone_number, full_name, email = None, **extra_fields):
    """
    Creates and returns a user with an phone,email and other fields.
    validate_email checks if a given string is a valid email address
    Validates phone number format using a regex pattern.
    """
    if not phone_number:
      raise ValidationError("Phone number is required")

    self.validate_phone_number(phone_number)

    if email:
      try:
        validate_email(email)  # Validate the email format
        email = self.normalize_email(email)
      except ValidationError:
        raise ValidationError("Invalid email format")
      
   
    user = self.model(
      phone_number=phone_number,
      full_name=full_name,
      email=email,
      **extra_fields
    )

    user.set_unusable_password() #Not using password login
    user.save()
    return user


  def create_superuser(self,full_name,phone_number, password,email = None, **extra_fields):
    """
    Creates and returns a superuser with an phone,email and other fields.
    """ 
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_superuser', True)
    if not password:
        raise ValidationError("Superuser must have a password.")

    superUser = self.create_user(
        phone_number=phone_number,  
        full_name=full_name,
        email=email,
        **extra_fields
    )

    superUser.set_password(password)  # Set the password for superuser
    superUser.save()
    
    return superUser

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that uses phone number as the unique identifier.
    No need to declare password field as it is inherited from AbstractBaseUser.
    The phone number is used as the username field.
    full name is a required field.
    Email is optional and can be left blank but should be unique if provided.
    The model also includes fields for staff status, superuser status, and active status.
    """
    email = models.EmailField(unique=True, blank=True, null=True)  # Optional email field
    phone_number = models.CharField(max_length=15, unique=True, blank = False)  # Unique phone number field
    full_name = models.CharField(max_length=255)  # Full name field
    is_staff = models.BooleanField(default=False)  # Staff status
    is_superuser = models.BooleanField(default=False)  # Superuser status
    is_active = models.BooleanField(default=True)  # Active status


    USERNAME_FIELD = 'phone_number'  # Use phone number as the unique identifier
    REQUIRED_FIELDS = ['full_name']  # Required fields for creating a user

    objects = CustomUserManager()  # Use the custom user manager

    def __str__(self):
        return self.full_name
