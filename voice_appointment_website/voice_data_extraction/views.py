from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
import whisper
import tempfile
import subprocess
import os
"""
    View to handle audio transcription requests.
    In Django REST Framework (DRF), parser classes are responsible for parsing the content of incoming HTTP requests into Python data types that your views can work with.
    MultiPartParser: Parses multipart form data (used for file uploads).
    The tempfile.NamedTemporaryFile function automatically creates a unique temporary file with a random name in the system’s temp directory.
"""
class AudioTranscriptionAPIView(APIView):

    parser_classes = [MultiPartParser]
    
    def post(self, request, *args, **kwargs):
        audio_file = request.FILES.get('audio') #Takes name of the field as argument
        if not audio_file:
            return Response({"error": "No audio file provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save the audio file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False,suffix = ".webm") as temp_audio: #delete=False means the file will not be deleted when closed as whisper needs to read it later
            for chunk in audio_file.chunks(): #reads the file in chunks to avoid memory issues with large files
                temp_audio.write(chunk)
            temp_audio.flush()
            temp_audio_input_path = temp_audio.name

        temp_output_fd,temp_output_audio_path = tempfile.mkstemp(suffix=".wav") # Create a temporary file for the output audio
        os.close(temp_output_fd)  # Close the file descriptor to avoid resource leaks
        try:
            """
            Convert audio to a format suitable for Whisper
            Subprocess allows to run external(shell) commands from Python.
            -i temp_audio_input_path: Specifies the input audio file.
            -ar 16000: Sets the audio sample rate to 16000 Hz, which is a common requirement for speech recognition models.
            -ac 1: Sets the number of audio channels to 1 (mono), which is often required for speech recognition tasks.
            -y: Overwrites the output file if it already exists.
            check = true: Raises an exception if the command fails.
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL: Suppresses the output of the command to avoid cluttering the console with ffmpeg logs.
            """
            subprocess.run([
                "ffmpeg","-y",
                "-i", temp_audio_input_path,  
                "-ar","16000",  
                "-ac","1",
                temp_output_audio_path
            ], check = True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # Suppress ffmpeg output

        


            # Load the Whisper model
            WhisperModel = whisper.load_model("base")  # You can change the model size as needed
            
            # Transcribe the audio file
            result = WhisperModel.transcribe(temp_output_audio_path) # result is a dictionary containing the transcription and other metadata

            # Return the transcription result
            return Response({"transcription": result['text']}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        finally:
            # Clean up the temporary file
            
            if os.path.exists(temp_audio_input_path):
                os.remove(temp_audio_input_path)
            if os.path.exists(temp_output_audio_path):
                os.remove(temp_output_audio_path)
    