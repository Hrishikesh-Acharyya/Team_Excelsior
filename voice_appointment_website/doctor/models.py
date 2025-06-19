from django.db import models

"""
Doctor model for storing doctor details.
Uses django's reverse relationship to link with AppointmentModel.
@property makes the function available as an attribute to get all appointments for a doctor.
"""

class DoctorModel(models.Model):
  photo = models.ImageField(upload_to='doctors/', default='doctors/default.jpg')
  name = models.CharField(max_length=100, unique=True)
  specialization = models.CharField(max_length=100)
  education = models.TextField()
  bio = models.TextField()
  experience = models.PositiveIntegerField(default=1)
  start_hour = models.TimeField(default = '09:00')
  lunch_start = models.TimeField(default = '13:00')
  lunch_end = models.TimeField(default = '15:00')
  evening_break_start = models.TimeField(default = '18:00')
  evening_break_end = models.TimeField(default = '18:15')
  end_hour = models.TimeField(default = '20:30')

  def __str__(self):
    return f"{self.name} - {self.specialization}"
  
  @property
  def appointments(self):
    return self.appointmentmodel_set.all()