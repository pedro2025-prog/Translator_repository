import os
import subprocess
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import threading
import time
import playsound

translator = Translator()

# Lock to synchronize threads for recording and playing sounds
recording_lock = threading.Lock()
playback_lock = threading.Lock()

def record_audio(file_name, duration=8):
    """Record audio using ffmpeg with output suppression"""
    command = f"ffmpeg -y -f alsa -i default -t {duration} {file_name} 2>/dev/null"
    subprocess.call(command, shell=True)

def recognize_and_translate(file_name, thread_id):
    """Recognize speech from a WAV file and translate it"""
    recognizer = sr.Recognizer()
    if not os.path.exists(file_name):
        print(f"File {file_name} does not exist.")
        return

    with sr.AudioFile(file_name) as source:
        # Adjust microphone sensitivity to ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=0.7)
        audio = recognizer.record(source)  # Read from the file

    try:
        # Convert speech to text
        text = recognizer.recognize_google(audio, language="pl-PL")
        
        # Check if recognized text is non-empty to avoid processing noise
        if text.strip():
            translated_text = translator.translate(text, src='pl', dest='uk').text

            # Output translated text to the console
            print(f"Translated Text (Thread {thread_id}): {translated_text}")

            # Convert translated text to speech using gTTS
            tts = gTTS(translated_text, lang='uk')
            audio_file = f"translated_{thread_id}_{time.time()}.mp3"
            tts.save(audio_file)
            
            # Play the generated speech, using playback lock to avoid overlaps
            with playback_lock:
                playsound.playsound(audio_file)

            # Optionally, delete the audio file after playback
            os.remove(audio_file)

    except sr.UnknownValueError:
        print(f"Thread {thread_id}: Speech could not be understood")
    except sr.RequestError as e:
        print(f"Thread {thread_id}: Speech recognition service error; {e}")

def recording_thread(thread_id, start_delay, duration=8, interval=12):
    """Thread function for recording with a delayed start"""
    max_files = 999
    file_index = 1

    time.sleep(start_delay)  # Delay before thread starts

    while True:
        file_name = f"output_{thread_id}_{file_index:03}_{time.time()}.wav"
        with recording_lock:
            record_audio(file_name, duration=duration)
        recognize_and_translate(file_name, thread_id)  # Recognize speech and translate with thread_id

        file_index += 1
        if file_index > max_files:
            file_index = 1  # Reset to file 001

        time.sleep(interval - duration)  # Wait before starting the next recording

if __name__ == "__main__":
    # Start two threads for speech processing
    threading.Thread(target=recording_thread, args=(1, 0, 8, 12), daemon=True).start()
    threading.Thread(target=recording_thread, args=(2, 6, 8, 12), daemon=True).start()

    # Keep the main thread running
    while True:
        time.sleep(1)
