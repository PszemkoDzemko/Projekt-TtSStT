import moviepy.editor as mp
import math

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