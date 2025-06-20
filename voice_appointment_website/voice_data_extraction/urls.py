from django.urls import path
from . import views

urlpatterns = [
  path('transcribe/', views.AudioTranscriptionAPIView.as_view(), name='AudioTranscription'),
  path('structure_data/', views.StructureDataAPIView.as_view(), name='StructureData'),
  path('validate-slot/', views.validate_slot, name='ValidateSlot'),
  path('available_slots/', views.available_slots, name='AvailableSlots'),
]