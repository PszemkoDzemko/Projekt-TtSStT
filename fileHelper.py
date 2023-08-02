import moviepy.editor as mp
import math
from youtube_transcript_api import YouTubeTranscriptApi
import json
import librosa
from scipy.io import wavfile
import os
import shutil
import Translate


# Get Audio from Video
def audioFromVideo(filepath):
    videoToAudio = mp.VideoFileClip(filepath)
    videoToAudio.audio.write_audiofile('files/audio.wav')
    return True


# Split audio file and export, used only if sttServie is google
def singleSplit(fromMin, toMin, splitFilename,newAudio):
    t1 = fromMin * 60 * 1000
    t2 = toMin * 60 * 1000
    splitAudio = newAudio[t1:t2]
    splitAudio.export("splitted/audio/"+splitFilename, format="wav")
def multipleSplit(minPerSplit,duration,newAudio):
    totalMins = math.ceil(duration/60)
    for i in range(0,totalMins, minPerSplit):
        splitFileN = str(i)+"-"+"audio.wav"
        singleSplit(i, i+minPerSplit, splitFileN,newAudio)
        if i == totalMins - minPerSplit:
            print('All splited successfully')

def getTranscript(ytLink,languageBatchDict,originalLang):
    splitted = False
    transcriptList = YouTubeTranscriptApi.list_transcripts(ytLink)
    print(transcriptList)
    transcript = transcriptList.find_transcript([originalLang,'en'])
    with open('files/transcriptOriginalEN.json','a', encoding='utf8') as f:
            json.dump(transcript.fetch(),f,ensure_ascii=False)
    for langNum, langData in languageBatchDict.items():
        transcriptLang = transcript.translate(langData['translation_target_language'])
        with open('files/transcript-'+langData['translation_target_language']+'.json','a', encoding='utf8') as f:
            json.dump(transcriptLang.fetch(),f,ensure_ascii=False)
        fileSize = os.stat('files/transcript-'+langData['translation_target_language']+'.json').st_size
        print(fileSize)
        if fileSize >= 5:
            with open('files/transcriptOriginalEN.json','r', encoding='utf-8') as f:
                file = json.load(f)
                text = ' '.join([item['text'] for item in file])
            splitted = sliceText(text)
        Translate.transcriptTranslate(languageBatchDict,splitted)
    return True


def lenghtCheck(languageBatchDict,duration):
    ogrAudioDuration = duration
    for langNum, langData in languageBatchDict.items():
        newAudio, sr = librosa.load('files/final-'+langData['translation_target_language']+'.wav')
        newAudioDuration = librosa.get_duration(y=newAudio,sr=sr)
        audioDif = ((newAudioDuration/ogrAudioDuration)*100)/100
        newFastAudio = librosa.effects.time_stretch(y=newAudio, rate=audioDif)
        wavfile.write('results/newAudio'+langData['translation_target_language']+'.wav',sr,newFastAudio)


def margeAudio(languageBatchDict):
    countAudioFile = 0
    for path in os.listdir(r'splitted/newAudio'):
        if os.path.isfile(os.path.join(r'splitted/newAudio',path)):
            countAudioFile += 1
    if countAudioFile<0:
        print('No file to marge')
        return
    clips =  []
    for langNum, langData in languageBatchDict.items():
        for i in range(int(countAudioFile/len(languageBatchDict))):
            clips.append(mp.AudioFileClip('splitted/newAudio/'+str(i)+'-newAudio-'+langData['translation_target_language']+'.wav'))
        newAudio = mp.concatenate_audioclips(clips)
        newAudio.write_audiofile('files/final-'+langData['translation_target_language']+'.wav')
        clips.clear()

def clearData():
    if os.path.exists('splitted'):
        shutil.rmtree('splitted')
    # uncomment later
    # if os.path.exists('files'):
    #     shutil.rmtree('files')
    if not os.path.exists('results'):
        os.mkdir('results')
    os.mkdir('splitted')
    # os.mkdir('files')
    for subfolder in ['audio', 'newAudio','text','translated','transcript']:
        os.makedirs(os.path.join('splitted', subfolder))
    return True


def sliceText(s):
    if len(s) <= 5000:
        return False
    else:
        a = 0
        for i in range(0, len(s), 5000):
            result = ""
            result = s[i:i+5000].rsplit(' ', 1)[0] + " "
            with open('splitted/transcript/transcriptSplitted-'+str(a)+'.txt','a', encoding='utf8') as f:
                f.write(result)
            a += 1
    return True