import os
import subprocess
import speech_recognition as sr
from googletrans import Translator
import tkinter as tk
import threading
import time

translator = Translator()

# Lists to store the last 10 texts
last_original_texts = []
last_translated_texts = []

# Lock to synchronize threads
recording_lock = threading.Lock()

def record_audio(file_name, duration=8):
    """Record audio using ffmpeg with output suppression"""
    command = f"ffmpeg -y -f alsa -i default -t {duration} {file_name} 2>/dev/null"
    subprocess.call(command, shell=True)

def recognize_and_translate(file_name):
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
        translated_text = translator.translate(text, src='pl', dest='no').text

        # Add texts to lists, limiting to the last 10 entries
        if len(last_original_texts) >= 10:
            last_original_texts.pop(0)
        last_original_texts.append(text)

        if len(last_translated_texts) >= 10:
            last_translated_texts.pop(0)
        last_translated_texts.append(translated_text)

        # Update the text in the window
        original_text_var.set("\n\n".join(last_original_texts))
        translated_text_var.set("\n\n".join(last_translated_texts))

    except sr.UnknownValueError:
        print("Speech could not be understood")
    except sr.RequestError as e:
        print(f"Speech recognition service error; {e}")

def recording_thread(thread_id, start_delay, duration=8, interval=12):
    """Thread function for recording with a delayed start"""
    max_files = 999
    file_index = 1

    time.sleep(start_delay)  # Delay before thread starts

    while True:
        file_name = f"output_{thread_id}_{file_index:03}.wav"
        with recording_lock:
            record_audio(file_name, duration=duration)
        recognize_and_translate(file_name)  # Recognize speech and translate

        file_index += 1
        if file_index > max_files:
            file_index = 1  # Reset to file 001

        time.sleep(interval - duration)  # Wait before starting the next recording

if __name__ == "__main__":
    # Initialize the Tkinter window
    root = tk.Tk()
    root.title("Speech Recognition and Translation")
    
    # Set the window size
    root.geometry("800x600")  # Increase window size

    # Variables to store text
    original_text_var = tk.StringVar()
    translated_text_var = tk.StringVar()

    # Frames to organize text
    frame_left = tk.Frame(root)
    frame_right = tk.Frame(root)

    frame_left.pack(side="left", padx=10, pady=10, fill="both", expand=True)
    frame_right.pack(side="right", padx=10, pady=10, fill="both", expand=True)

    # Labels to display text
    original_label = tk.Label(frame_left, textvariable=original_text_var, font=("Helvetica", 16), wraplength=400, justify="left")
    translated_label = tk.Label(frame_right, textvariable=translated_text_var, font=("Helvetica", 16), wraplength=400, justify="left")

    original_label.pack(pady=10)
    translated_label.pack(pady=10)

    # Start two threads for speech processing
    threading.Thread(target=recording_thread, args=(1, 0, 6, 10), daemon=True).start()
    threading.Thread(target=recording_thread, args=(2, 5, 6, 10), daemon=True).start()

    root.mainloop()



"""
Targel langauge

Common Language Codes for Speech Recognition (recognize_google):
English (United States): en-US
English (United Kingdom): en-GB
Spanish (Spain): es-ES
Spanish (Mexico): es-MX
French (France): fr-FR
French (Canada): fr-CA
German: de-DE
Italian: it-IT
Russian: ru-RU
Portuguese (Brazil): pt-BR
Portuguese (Portugal): pt-PT
Chinese (Mandarin): zh-CN
Japanese: ja-JP
Korean: ko-KR
Arabic: ar-SA
Dutch: nl-NL
Hindi: hi-IN
Turkish: tr-TR
Swedish: sv-SE
Polish: pl-PL
Greek: el-GR
Hebrew: he-IL
Danish: da-DK
Finnish: fi-FI
Norwegian: no-NO
Czech: cs-CZ
Hungarian: hu-HU

Common Language Codes for Translation (translator.translate):
Afrikaans: af
Albanian: sq
Amharic: am
Arabic: ar
Armenian: hy
Azerbaijani: az
Basque: eu
Belarusian: be
Bengali: bn
Bosnian: bs
Bulgarian: bg
Catalan: ca
Cebuano: ceb
Chinese (Simplified): zh-CN
Chinese (Traditional): zh-TW
Corsican: co
Croatian: hr
Czech: cs
Danish: da
Dutch: nl
English: en
Esperanto: eo
Estonian: et
Finnish: fi
French: fr
Frisian: fy
Galician: gl
Georgian: ka
German: de
Greek: el
Gujarati: gu
Haitian Creole: ht
Hausa: ha
Hawaiian: haw
Hebrew: he
Hindi: hi
Hmong: hmn
Hungarian: hu
Icelandic: is
Igbo: ig
Indonesian: id
Irish: ga
Italian: it
Japanese: ja
Javanese: jv
Kannada: kn
Kazakh: kk
Khmer: km
Kinyarwanda: rw
Korean: ko
Kurdish: ku
Kyrgyz: ky
Lao: lo
Latin: la
Latvian: lv
Lithuanian: lt
Luxembourgish: lb
Macedonian: mk
Malagasy: mg
Malay: ms
Malayalam: ml
Maltese: mt
Maori: mi
Marathi: mr
Mongolian: mn
Myanmar (Burmese): my
Nepali: ne
Norwegian: no
Nyanja (Chichewa): ny
Odia (Oriya): or
Pashto: ps
Persian: fa
Polish: pl
Portuguese: pt
Punjabi: pa
Romanian: ro
Russian: ru
Samoan: sm
Scots Gaelic: gd
Serbian: sr
Sesotho: st
Shona: sn
Sindhi: sd
Sinhala (Sinhalese): si
Slovak: sk
Slovenian: sl
Somali: so
Spanish: es
Sundanese: su
Swahili: sw
Swedish: sv
Tagalog (Filipino): tl
Tajik: tg
Tamil: ta
Tatar: tt
Telugu: te
Thai: th
Turkish: tr
Turkmen: tk
Ukrainian: uk
Urdu: ur
Uyghur: ug
Uzbek: uz
Vietnamese: vi
Welsh: cy
Xhosa: xh
Yiddish: yi
Yoruba: yo
Zulu: zu


"""