import os
import subprocess
import speech_recognition as sr
from googletrans import Translator
import threading
import time

translator = Translator()

# Lock to synchronize threads
recording_lock = threading.Lock()

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
        audio = recognizer.record(source)  # Read from the file

    try:
        # Convert speech to text
        text = recognizer.recognize_google(audio, language="pl-PL")
        translated_text = translator.translate(text, src='pl', dest='en').text

        # Output translated text to the console
        print(f"Translated Text (Thread {thread_id}): {translated_text}")

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
        file_name = f"output_{thread_id}_{file_index:03}.wav"
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
