import os
import json
from gtts import gTTS
import fileHelper
import azure.cognitiveservices.speech as speechsdk

def googleTTS(languageBatchDict, serviceSTT, transcriptExists):
    if serviceSTT == 'google' and not transcriptExists:
        countAudioFile = 0
        countTranslatedFile = 0
        countNewAudioFile = 0 
        for path in os.listdir(r'splitted/audio'):
            if os.path.isfile(os.path.join(r'splitted/audio',path)):
                countAudioFile += 1
        for path in os.listdir(r'splitted/translated'):
            if os.path.isfile(os.path.join(r'splitted/translated',path)):
                countTranslatedFile += 1
        for path in os.listdir(r'splitted/newAudio'):
            if os.path.isfile(os.path.join(r'splitted/newAudio',path)):
                countNewAudioFile += 1
        if countTranslatedFile<0:
            print('No file')
            return
        if countNewAudioFile>0:
            print('There are files in spilitted/newAudio directory')
            return
        for i in range(countAudioFile):
            for langNum, langData in languageBatchDict.items():
                with open('splitted/translated/'+str(i)+'-text-'+langData['translation_target_language']+'.txt','r', encoding='utf-8') as f:
                    file = f.readlines()
                newLangAudio = gTTS(text=str(file),lang=langData['translation_target_language'],slow=False)
                newLangAudio.save('splitted/newAudio/'+str(i)+'-newAudio-'+langData['translation_target_language']+'.wav')
        return
    # TTS for other STT than google
    if transcriptExists:
        print(transcriptExists)
        for langNum, langData in languageBatchDict.items():
            with open('files/transcript-'+langData['translation_target_language']+'.json','r', encoding='utf-8') as f:
                file = json.load(f)
                text = ''.join([item['text'] for item in file])
            newLangAudio = gTTS(text=text,lang=langData['translation_target_language'],slow=False)
            newLangAudio.save('files/final-'+langData['translation_target_language']+'.wav')
        return

    if serviceSTT is not 'google' and not transcriptExists:
        for langNum, langData in languageBatchDict.items():
            with open('files/text-'+langData['translation_target_language']+'.txt','r', encoding='utf-8') as f:
                file = f.readlines()
            newLangAudio = gTTS(text=str(file),lang=langData['translation_target_language'],slow=False)
            newLangAudio.save('files/final-'+langData['translation_target_language']+'.wav')
        return

def azureTTS(languageBatchDict,api_key,azureRegion):
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get(api_key), region=os.environ.get(azureRegion))
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    with open('files/transcript-'+langData['translation_target_language']+'.json','r', encoding='utf-8') as f:
            file = json.load(f)
            text = ''.join([item['text'] for item in file])
    for langNum, langData in languageBatchDict.items():
        speech_config.speech_synthesis_voice_name=langData['synth_voice_name']
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            with open('files/final-'+langData['translation_target_language']+'.wav', "wb") as f:
                f.write(speech_synthesis_result.audio_data)
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
                    print("Did you set the speech resource key and region values?")


def transcriptTTS(languageBatchDict):
    countTranslatedFile = 0
    for path in os.listdir(r'splitted/translated'):
        if os.path.isfile(os.path.join(r'splitted/translated',path)):
            countTranslatedFile += 1
    if countTranslatedFile>0:
        for i in range(countTranslatedFile):
            for langNum, langData in languageBatchDict.items():
                with open('splitted/translated/'+str(i)+'-text-'+langData['translation_target_language']+'.txt','r', encoding='utf-8') as f:
                    file = f.readlines()
                newLangAudio = gTTS(text=str(file),lang=langData['translation_target_language'],slow=False)
                newLangAudio.save('splitted/newAudio/'+str(i)+'-newAudio-'+langData['translation_target_language']+'.wav')
        fileHelper.margeAudio(languageBatchDict)
    if countTranslatedFile<1:
        for langNum, langData in languageBatchDict.items():
            with open('files/transcript-'+langData['translation_target_language']+'.json','r', encoding='utf-8') as f:
                file = json.load(f)
                text = ''.join([item['text'] for item in file])
            newLangAudio = gTTS(text=text,lang=langData['translation_target_language'],slow=False)
            newLangAudio.save('files/final-'+langData['translation_target_language']+'.wav')