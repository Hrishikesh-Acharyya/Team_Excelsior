"""
This module uses the Whisper library to transcribe audio files.
It loads the Whisper model and provides functionality to transcribe audio data.
declaring it this way allows for easy integration with Django views.
It also means the model needs to be loaded only once when the server starts,
which is more efficient than loading it for every request.
"""

import whisper

model = whisper.load_model("tiny") # tiny, base, small, medium, large