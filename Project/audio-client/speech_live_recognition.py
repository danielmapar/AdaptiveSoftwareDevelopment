#!/usr/bin/env python3
import speech_recognition as sr

r = sr.Recognizer()

print(sr.Microphone.list_microphone_names())
mic = sr.Microphone(device_index=7) # Internal mic

with mic as source:
    audio = r.listen(source)

print(r.recognize_google(audio))

# r = sr.Recognizer()
#
# harvard = sr.AudioFile('audio_files/jackhammer.wav')
# with harvard as source:
#     r.adjust_for_ambient_noise(source, duration=0.5)
#     audio = r.record(source)
#
# print(r.recognize_google(audio, show_all=True))
