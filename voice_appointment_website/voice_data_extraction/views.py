from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
import whisper
import tempfile
import subprocess
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
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

        #TODO: Handle cleanup of temporary files in case of errors or crashes. Implement it
        finally:
            # Clean up the temporary file
            
            if os.path.exists(temp_audio_input_path):
                os.remove(temp_audio_input_path)
            if os.path.exists(temp_output_audio_path):
                os.remove(temp_output_audio_path)


class StructureDataAPIView(APIView):
    """
    View to send the transcribed data to the llama api for structuring the data.
    """
    def post(self, request, *args, **kwargs):
        transcription = request.data.get('transcription')
        if not transcription:
            return Response({"error": "No transcription provided."}, status=status.HTTP_400_BAD_REQUEST)

        structured_data = self.call_llm(transcription)
        if isinstance(structured_data, Response): # if the call_llm function returns a Response object which it does in case of error , return it directly
            return structured_data
        return Response(structured_data, status=status.HTTP_200_OK)
    
    def call_llm(self, transcription):
        """
        Call the Together.ai Llama API to structure the data.
        """
        api_key = os.getenv("TOGETHER_AI_API_KEY")
        endpoint = os.getenv("TOGETHER_AI_API_URL")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        prompt = f"""
        You are an intelligent assistant at a well known hospital that extracts structured data from voice-to-text medical appointment requests.
        Be smart. Since the transcription is from a voice message, it may contain incomplete or unclear information. If you can smartly infer the missing information, do so.
        If you cannot infer the missing information, set it to null.
        ⚠️ If the user spells out their name or email using letters (e.g., H-A-R-R-Y), always prefer the spelled version over any earlier guess. Remove the hyphens and spaces from the spelled version to get the final name or email.

        Given the following user message:
        \"\"\"{transcription}\"\"\"

        Extract the relevant information and return ONLY valid JSON with the following keys:
        - "intent": One of ["book", "reschedule", "cancel"].
        - "name": Full name of the patient. The patient may spell it out (if mentioned, otherwise null),
        - "age": Age of the patient (if mentioned, otherwise null),
        - "gender": Gender of the patient (if mentioned, otherwise null),
        - "symptoms": Any symptoms the user has like(fever, cough, etc.), how long he has been suffering, any medical concerns etc (if mentioned, otherwise null),
        - "phone": Phone number of the patient (if mentioned, otherwise null),
        - "email": Email address of the patient (if mentioned, otherwise null), infer the email from the context the name of user. Usually emails are name/surname@domain.com. Infer the domain properly. Consider only well known domains like gmail.com, yahoo.com, outlook.com etc. If not mentioned, set it to null.
        - "doctor": Name  of the doctor (if mentioned, otherwise null),
        - "specialization": Specialization of the doctor (if mentioned, otherwise null),
        - "datetime": Appointment date and time in ISO 8601 format (e.g., "2025-06-18T14:00:00"). If they say X days from now, calculate the date and time accordingly. If not mentioned, set it to null.
        

        Do not include any explanation or commentary. Only respond with the JSON object.

        If a field is missing or unclear, set its value to null.
        """

        body = {
            "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",  # Specify the model you want to use
            "messages":[
                {"role": "system", "content": "You are an intelligent assistant at a well known hospital that extracts structured data from voice-to-text natural language medical appointment requests."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4  # Adjust as needed
        }

        try: 
            response = requests.post(endpoint, headers=headers, data=json.dumps(body))
            response.raise_for_status()

            content = response.json()['choices'][0]['message']['content']
            return json.loads(content)
        except requests.exceptions.RequestException as e:
            print(f"Error calling Together.ai API: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)