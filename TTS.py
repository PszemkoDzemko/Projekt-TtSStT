import os
from gtts import gTTS


def googleTTS(languageBatchDict, serviceSTT):
    if serviceSTT == 'google':
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
    for langNum, langData in languageBatchDict.items():
        with open('files/text-'+langData['translation_target_language']+'.txt','r', encoding='utf-8') as f:
            file = f.readlines()
        newLangAudio = gTTS(text=str(file),lang=langData['translation_target_language'],slow=False)
        newLangAudio.save('files/newAudio-'+langData['translation_target_language']+'.wav')

def azureTTS():
    print('azure TTS')