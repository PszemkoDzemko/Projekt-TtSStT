import os
import speech_recognition as sr
from threading import Thread

r = sr.Recognizer()


def googleSTT(lang):
    countAudioFile = 0
    countTextFile = 0
    for path in os.listdir(r'splitted/audio'):
        if os.path.isfile(os.path.join(r'splitted/audio',path)):
            countAudioFile += 1
    for path in os.listdir(r'splitted/text'):
        if os.path.isfile(os.path.join(r'splitted/text',path)):
            countTextFile += 1
    if countTextFile>0:
        print("There are files in spilitted/text directory")
        return
    for i in range(countAudioFile):
        with sr.AudioFile("splitted/audio/"+str(i)+"-audio.wav") as source:
            r.adjust_for_ambient_noise(source) 
            audio = r.record(source)
        try:
            result = r.recognize_google(audio,language=lang)
            with open('splitted/text/'+str(i)+'-text.txt','a', encoding='utf8') as f:
                f.write(result)
        except sr.UnknownValueError:
            print("Google could not understand audio")
        except sr.RequestError as e:
            print("Google error; {0}".format(e))


def googleCloudSTT(audio, GOOGLE_CLOUD_SPEECH_CREDENTIALS):
    try:
        result = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)
        with open('files/text.txt','a', encoding='utf8') as f:
            f.write(result)
    except sr.UnknownValueError:
        print("Google Cloud Speech could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Cloud Speech service; {0}".format(e))

def azureSTT(audio,AZURE_SPEECH_KEY):
    try:
        result = r.recognize_azure(audio, key=AZURE_SPEECH_KEY)
        with open('files/text.txt','a', encoding='utf8') as f:
            f.write(result)
    except sr.UnknownValueError:
        print("Microsoft Azure Speech could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Microsoft Azure Speech service; {0}".format(e))