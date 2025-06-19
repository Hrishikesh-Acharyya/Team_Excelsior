/**
 * This script handles audio recording functionality for a web application.
 * It allows users to start and stop audio recording, and processes the recorded audio.
 * It uses the MediaRecorder API to capture audio from the user's microphone.
 */
const defaultRecordingTime = 2*60*1000
const toggleMicButton = document.getElementById('toggle-mic-button');
const nameField = document.getElementById('name');
const ageField = document.getElementById('age');
const genderField = document.getElementById('gender');
const phoneField = document.getElementById('phone');
const symptomsField = document.getElementById('symptoms');
const emailField = document.getElementById('email');

let mediaRecorder;
let audioChunks = [];
let is_recording = false;
let timeout_record_ID = null; // Variable to store the timeout ID for stopping the recording after a certain time

toggleMicButton.addEventListener('click', Toggle);

/**
 * Sets up audio recording using the MediaRecorder API.
 * First checks if the browser supports the necessary APIs.
 * If supported, it requests access to the user's microphone.
 * Initializes the MediaRecorder with the audio stream.
 * navigator.mediaDevices is the API for accessing media devices (like microphone/camera).
 * navigator.mediaDevices.getUserMedia is the function used to request access to the microphone.
 */

async function setupAudioRecording() {

    console.log("Setting up audio recording...");
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert("Audio recording not supported in this browser.");
        return false;
    }
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
    } catch (error) {
        if (error.name === 'NotAllowedError') {
            alert("Microphone access denied. Please allow microphone access to record audio.");
        } else {
            alert("Error accessing microphone: " + error.message);
        }

         return false;
    }
    return true;
}

/**
 * Handles the toggle functionality
 * Contains code for starting and stopping the audio recording.
 * When recording is active sets is_recording to false and updates the button text and vice versa
 * When recording stops, it processes the audio data and stores it in browser RAM.
 */


//TODO: Add Auto Chuncking

async function Toggle() {
    if (is_recording) {
        clearTimeout(timeout_record_ID);
        timeout_record_ID = null; // Clear the timeout ID when stopping recording
        toggleMicButton.textContent = "Start Talking";
        console.log("Stopping audio recording...");
        mediaRecorder.stop();
        is_recording = false;

    } else if (!is_recording && await setupAudioRecording()) { // await so  the function waits for the setup to complete before proceeding
        console.log("Starting audio recording...");
        is_recording = true;
        toggleMicButton.textContent = "Stop Recording";
        mediaRecorder.start(); //start recording
        audioChunks = []; //As the recording goes on, the MediaRecorder periodically emits dataavailable events. Audio made available in small chunks
        console.log("Recording started...");

    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' }); //blob is binary large object, used to store audio data
        console.log("Recording stopped, processing audio...");
        sendAudioToBackend(audioBlob); //send the audio blob to the backend for processing
 
     };

        timeout_record_ID = setTimeout(() => {
        console.log("Time ran out")
        is_recording = false;
        toggleMicButton.textContent = "Start Talking";
        mediaRecorder.stop();

    }, defaultRecordingTime); // Record for 2 minutes, adjust as needed
}
};

/**
 * Sends the recorded audio blob to the backend for processing.
 * sending to endpoint 'voice_data_extraction/transcribe/' using fetch API.
 * The audio blob is wrapped in a FormData object to handle file uploads.
 * FormData is a built-in JavaScript object that lets you easily construct a set of key/value pairs representing form fields and their values, including files (like audio or images). 
 * It is commonly used to send data to a server via fetch or XMLHttpRequest using the multipart/form-data encoding.
 * @param {Blob} audioBlob 
 */

// TODO: Review if cors needed

async function sendAudioToBackend(audioBlob)
{
    const audioFile = new File([audioBlob], 'recording.wav', { type: 'audio/wav' });
    const formData = new FormData();
    formData.append('audio', audioFile); //Name of the field in the form data is 'audio'

    try {
        const response = await fetch(`${HOST_NAME}/voice_data_extraction/transcribe/`, {
            method: 'POST',
            body: formData,
        });
        console.log("data recieved")
        const data = await response.json();
        console.log(JSON.stringify(data.transcription));
        if (data.transcription) {
            showTranscription(data,false);
           // alert('Transcription: ' + data.transcription);
        } else {
            // Handle empty transcription
            showTranscription(data,true);
        }
    } catch (error) {
        console.error('Error sending audio to backend:', error);
    }
}

/**
 * Displays the transcription result in the UI.
 * @param {Object} data - The response data from the backend.
 * @param {boolean} is_empty - Indicates if the transcription is empty.
 */

function showTranscription(data,is_empty) {
    const transcriptionContainer = document.getElementById('transcription');

    if( is_empty) {
        transcriptionContainer.innerHTML =
            `<div>
                <p id="prev-transcript">Transcription: Sorry!! Did not quite get that</p>
                <p>Press the button to record again</p>
            </div>`;
    } else {
        transcriptionContainer.innerHTML =
            `<div>
                <p id="prev-transcript">Transcription: ${data.transcription}</p>
                <p>Press the button to record again or edit any field </p>
            </div>`;
        structureData(data)
    }

   

}
/**
 * Takes the whisperAI response and sends it to backend for further processing.
 * This function is called after the audio has been transcribed and the transcription is available.
 * @param {Object} data  - The response data from the backend containing the transcription.
 */
async function structureData(data) {

    try {
        const structuredResponse = await fetch(`${HOST_NAME}/voice_data_extraction/structure_data/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!structuredResponse.ok) {
            throw new Error('Failed to send structured data');
        }

        console.log('Structured data sent successfully');

        const structuredData = await structuredResponse.json();
        console.log('Structured Data:', structuredData);
        console.log("displayStructuredData called")
        
        displayStructuredData(structuredData);
    } catch (error) {
        console.error('Error sending structured data:', error);
    }
}

function displayStructuredData(structuredData) {
    if (structuredData.name !== null && structuredData.name !== undefined) nameField.value = structuredData.name;
    if (structuredData.age !== null && structuredData.age !== undefined) ageField.value = structuredData.age;
    if (structuredData.gender !== null && structuredData.gender !== undefined) genderField.value = structuredData.gender;
    if (structuredData.phone !== null && structuredData.phone !== undefined) phoneField.value = structuredData.phone;
    if (structuredData.symptoms !== null && structuredData.symptoms !== undefined) symptomsField.value = structuredData.symptoms;
    if (structuredData.email !== null && structuredData.email !== undefined) emailField.value = structuredData.email;
}

// document.addEventListener("DOMContentLoaded", () => {
//     if (isLoggedIn) {
//         // Disable fields that should come from user info
//         //nameField.readOnly = true;
//         phoneField.readOnly = true;
//     }
// });
