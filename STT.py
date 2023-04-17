import configparser
import moviepy.editor as mp
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import math
from pydub import AudioSegment
import os
import librosa
from scipy.io import wavfile

# Read config files
config = configparser.ConfigParser(allow_no_value=True)
config.read('config.ini')
cloudConfig = configparser.ConfigParser()
cloudConfig.read('cloud_service_settings.ini')
batchConfig = configparser.ConfigParser()
batchConfig.read('batch.ini')

# Get variables from config
sttService = cloudConfig['CLOUD']['stt_service'].lower()
ttsService = cloudConfig['CLOUD']['tts_service'].lower()
translateService = cloudConfig['CLOUD']['translate_service'].lower()
videoFilepath = config['SETTINGS']['original_video_file_path'].lower()
audioFilepath = config['SETTINGS']['orginal_audio_file_path'].lower()
audioFileExists = config.getboolean('SETTINGS','audio_file_exists')
languageNums = batchConfig['BATCH']['enabled_languages'].replace(' ','').split(',')
originalLang = config['SETTINGS']['original_language']

batchSettings = {}
for num in languageNums:
    batchSettings[num] = {
        'translation_target_language': batchConfig[f'LANGUAGE-{num}']['translation_target_language'],
        'synth_language_code': batchConfig[f'LANGUAGE-{num}']['synth_language_code'],
        'synth_voice_name': batchConfig[f'LANGUAGE-{num}']['synth_voice_name'],
        'synth_voice_gender': batchConfig[f'LANGUAGE-{num}']['synth_voice_gender']
    }

# Get audio from video file
if not audioFileExists:
    videoToAudio = mp.VideoFileClip(videoFilepath)
    videoToAudio.audio.write_audiofile(audioFilepath)
    config['SETTINGS']['audio_file_exists'] = 'yes'
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# Set audio file from path
AUDIO_FILE = audioFilepath

# Asign recognizer
r = sr.Recognizer()

# Split audio file and export, used only if sttServie is google
def singleSplit(fromMin, toMin, splitFilename):
    t1 = fromMin * 60 * 1000
    t2 = toMin * 60 * 1000
    splitAudio = newAudio[t1:t2]
    splitAudio.export("splitted/audio/"+splitFilename, format="wav")
def multipleSplit(minPerSplit):
    totalMins = math.ceil(duration/60)
    for i in range(0,totalMins, minPerSplit):
        splitFileN = str(i)+"-"+"audio.wav"
        singleSplit(i, i+minPerSplit, splitFileN)
        if i == totalMins - minPerSplit:
            print('All splited successfully')
            return

# Marge audio files into 1 file
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

# Check audio lenght
def lenghtCheck(languageBatchDict):
    orgAudio = AudioSegment.from_wav(AUDIO_FILE)
    ogrAudioDuration = orgAudio.duration_seconds
    for langNum, langData in languageBatchDict.items():
        newAudio, sr = librosa.load('files/final-'+langData['translation_target_language']+'.wav')
        newAudioDuration = librosa.get_duration(newAudio)
        audioDif = ((newAudioDuration/ogrAudioDuration)*100)/100
        newFastAudio = librosa.effects.time_stretch(newAudio, audioDif)
        wavfile.write('newAudioFast'+langData['translation_target_language']+'.wav',sr,newFastAudio)

 
# Google Speech to text service  
def googleSTT():
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
    if countAudioFile<=0:
        multipleSplit(1)
    for i in range(countAudioFile):
        with sr.AudioFile("splitted/audio/"+str(i)+"-audio.wav") as source:
            r.adjust_for_ambient_noise(source) 
            audio = r.record(source)
        try:
            result = r.recognize_google(audio,language='en')
            with open('splitted/text/'+str(i)+'-text.txt','a', encoding='utf8') as f:
                f.write(result)
        except sr.UnknownValueError:
            print("Google could not understand audio")
        except sr.RequestError as e:
            print("Google error; {0}".format(e))

# Translation with google
def googleTranslate(languageBatchDict):
    if sttService == 'google':
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

# Text to speech Google
def googleTTS(languageBatchDict):
    if sttService == 'google':
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
        margeAudio(batchSettings)
        return
    # TTS for other STT than google
    for langNum, langData in languageBatchDict.items():
        with open('files/text-'+langData['translation_target_language']+'.txt','r', encoding='utf-8') as f:
            file = f.readlines()
        newLangAudio = gTTS(text=str(file),lang=langData['translation_target_language'],slow=False)
        newLangAudio.save('files/newAudio-'+langData['translation_target_language']+'.wav')


# Check if speech to text service is google
if sttService == 'google':
    newAudio = AudioSegment.from_wav(AUDIO_FILE)
    duration = newAudio.duration_seconds
    googleSTT()

# Check if translation service is google
if translateService == 'google':
    googleTranslate(batchSettings)

# Check if Text to speech service is google
if ttsService == 'google':
    googleTTS(batchSettings)
    
lenghtCheck(batchSettings)