import wave
import pyaudio
import os
import time
import speech_recognition as sr
import requests
import urllib.parse
import winsound

class Audio:
    def __init__(self):
        self.recording = False
        self.input_filename = "input.wav"
        self.output_filename = "misaka.wav"

    def transcribe_audio(self):
        r = sr.Recognizer()
        audio = sr.AudioFile(self.input_filename)
        with audio as source:
            f = r.record(source)
        sentence = r.recognize_google(f)
        return sentence

    def record_audio(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        frames = []
        print("Recording...")
        while self.recording:
            data = stream.read(CHUNK)
            frames.append(data)
        print("Stopped recording.")
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf = wave.open(self.input_filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

    def voicevox_tts(self, text):
        # You need to run docker first and run the command bellow, it does automatically download voicevox image file for docker for first time:
        # Choose one between cpu or gpu which suitable for your device:
        # cpu : docker run --rm -it -p 50021:50021 voicevox/voicevox_engine:cpu-ubuntu20.04-latest
        # gpu : docker run --rm --gpus all -p 50021:50021 voicevox/voicevox_engine:nvidia-ubuntu20.04-latest
        # Convert the text to katakana for better voice so it more sounds natural
        # I dont do the convert, just translate with googleTrans so that may sounds wrong japanesse. i so lazy :)
        # The official website https://voicevox.hiroshiba.jp
        #for speaker model, pls check the speaker.json and change the number in 'speaker':6
        try:
            voicevox_url = 'http://localhost:50021'
            params_encoded = urllib.parse.urlencode({'text': text, 'speaker': 6})
            request = requests.post(f'{voicevox_url}/audio_query?{params_encoded}')
            params_encoded = urllib.parse.urlencode({'speaker': 6, 'enable_interrogative_upspeak': True})
            request = requests.post(f'{voicevox_url}/synthesis?{params_encoded}', json=request.json())

            with open(self.output_filename, "wb") as outfile:
                outfile.write(request.content)
        except:
            print("make sure the voicevox docker was running...")
            print("Please, check audio.py in utils folder. see at voicevox_tts() function")
    def play_audio(self):
        try:
            winsound.PlaySound(self.output_filename, winsound.SND_FILENAME)
            time.sleep(1)
            os.remove(self.output_filename)
        except:
            print("There is no sound (misaka.wav)....")

