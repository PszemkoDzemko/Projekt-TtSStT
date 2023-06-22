import moviepy.editor as mp
import math
from youtube_transcript_api import YouTubeTranscriptApi
import json
import librosa
from scipy.io import wavfile
import os

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

def getTranscript(ytLink,languageBatchDict):
    transcriptList = YouTubeTranscriptApi.list_transcripts(ytLink)
    print(transcriptList)

    transcript = transcriptList.find_transcript(['en'])
    for langNum, langData in languageBatchDict.items():
        transcriptLang = transcript.translate(langData['translation_target_language'])
        print(transcriptLang.fetch())
        with open('files/transcript-'+langData['translation_target_language']+'.json','a', encoding='utf8') as f:
            json.dump(transcriptLang.fetch(),f,ensure_ascii=False)


def lenghtCheck(languageBatchDict,duration,):
    ogrAudioDuration = duration
    for langNum, langData in languageBatchDict.items():
        newAudio, sr = librosa.load('files/final-'+langData['translation_target_language']+'.wav')
        newAudioDuration = librosa.get_duration(newAudio)
        audioDif = ((newAudioDuration/ogrAudioDuration)*100)/100
        newFastAudio = librosa.effects.time_stretch(newAudio, audioDif)
        wavfile.write('newAudioFast'+langData['translation_target_language']+'.wav',sr,newFastAudio)

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
