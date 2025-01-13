import os
import speech_recognition as sr 
import gtts 
from playsound import playsound
from os import path
from pydub import AudioSegment

r = sr.Recognizer()


def get_audio():
    with sr.Microphone() as source:
        print("Say something")
        audio = r.listen(source)
    
    return audio 


def audio2text(audio):
    text = ""
    try:
        text = r.recognize_google(audio, language='en-GB')
        # text = r.recognize_sphinx(audio,language='en-GB')
    except sr.UnknownValueError:
        print("Speech recognition can't understand audio")
    except sr.RequestError:
        print("could not request results from API")

    return text 


def play_sound(text):
    try:
        tts = gtts.gTTS(text)
        tempfile = "./temp.mp3"
        tts.save(tempfile)
        playsound(tempfile)
        os.remove(tempfile)
    except AssertionError:
        print("could not play sound")


if __name__ == "__main__":
    tts = gtts.gTTS("what can I do for you ?")
    print(tts)
    tempfile = "./temp.mp3"
    tts.save(tempfile)
    with open(tempfile, 'rb') as f:
        audio = sr.AudioData(f.read(), 16000, 2)
    print(audio)


    # files
    src = "./temp.mp3"
    dst = "./temp.wav"

    # convert from mp3 to wav
    sound = AudioSegment.from_mp3(src)
    sound.export(dst, format="wav")
    # playsound(tempfile)
    # os.remove(tempfile)

    # print(audio2text(audio))
