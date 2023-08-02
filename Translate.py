import os
import json
from deep_translator import GoogleTranslator,MicrosoftTranslator,DeeplTranslator

def googleTranslate(languageBatchDict, serviceSTT):
    if serviceSTT == 'google':
        countTextFile = 0
        countTranslatedFile = 0
        for path in os.listdir(r'splitted/text'):
            if os.path.isfile(os.path.join(r'splitted/text',path)):
                countTextFile += 1
        for path in os.listdir(r'splitted/translated'):
            if os.path.isfile(os.path.join(r'splitted/translated',path)):
                countTranslatedFile += 1
        if countTextFile<=0:
            print('No file to translate')
            return
        if countTranslatedFile>0:
            print('There are files in spilitted/translated directory')
            return
        for i in range(countTextFile):
            for langNum, langData in languageBatchDict.items():
                result = GoogleTranslator(source='auto',target=langData['translation_target_language']).translate_file(r'splitted/text'+'/'+str(i)+'-text.txt')
                with open('splitted/translated/'+str(i)+'-text-'+langData['translation_target_language']+'.txt','a', encoding='utf-8') as f:
                    f.writelines(result)
        return
    # Translation for other STT than google
    for langNum, langData in languageBatchDict.items():
        result = GoogleTranslator(source='auto',target=langData['translation_target_language']).translate_file(r'files/'+'text.txt')
        with open('files/text-'+langData['translation_target_language']+'.txt','a', encoding='utf-8') as f:
            f.writelines(result)


def azureTranslate(languageBatchDict,api_key,):
    for langNum, langData in languageBatchDict.items():
        result = MicrosoftTranslator(api_key=api_key, target=langData['translation_target_language']).translate_file(r'files/'+'text.txt')
        with open('files/text-'+langData['translation_target_language']+'.txt','a', encoding='utf-8') as f:
            f.writelines(result)
            
def deepLTranslate(languageBatchDict,api_key):
    for langNum, langData in languageBatchDict.items():
        result = DeeplTranslator(api_key=api_key, use_free_api=True, target=langData['translation_target_language']).translate_file(r'files/'+'text.txt')
        with open('files/text-'+langData['translation_target_language']+'.txt','a', encoding='utf-8') as f:
            f.writelines(result)

def transcriptTranslate(languageBatchDict,splitted):
    if splitted:
        countTranscriptFile = 0
        for path in os.listdir(r'splitted/transcript'):
            if os.path.isfile(os.path.join(r'splitted/transcript',path)):
                countTranscriptFile += 1
        for i in range(countTranscriptFile):
            for langNum, langData in languageBatchDict.items():
                result = GoogleTranslator(source='auto',target=langData['translation_target_language']).translate_file(r'splitted/transcript/transcriptSplitted-'+str(i)+'.txt')
                with open('splitted/translated/'+str(i)+'-text-'+langData['translation_target_language']+'.txt','a', encoding='utf-8') as f:
                    f.writelines(result)
    if not splitted:
        for langNum, langData in languageBatchDict.items():
            with open('files/transcriptOriginalEN.json','r', encoding='utf-8') as f:
                file = json.load(f)
                text = ' '.join([item['text'] for item in file])
            result = GoogleTranslator(source='auto',target=langData['translation_target_language']).translate_file(r'files/transcriptOriginalEN.json')
            with open('files/text-'+langData['translation_target_language']+'.txt','a', encoding='utf-8') as f:
                f.writelines(result)
