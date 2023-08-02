import tkinter
import configparser
import customtkinter
import pathlib
import fileHelper
import newSTT
import Translate
import TTS
from tkinter import filedialog as fd
from pydub import AudioSegment
from pytube import YouTube
import os

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")

# Variables
cloudConfig = None
errorMessages = None
batchConfig = configparser.ConfigParser(allow_no_value=True)
batchConfig.read('batch.ini')
languageNums = batchConfig['BATCH']['lang_num']
batchSettings = {}
for i in range(int(languageNums)):
    batchSettings[i] = {
        'lang_name': batchConfig[f'LANGUAGE-{i}']['lang_name']
    }
langSettings = {}
originalLang = 'en-US'
orgFilePath = ''
ytLink = ''
serviceSTT = 'google'
serviceTranslate = 'google'
serviceTTS = 'google'
googleCloudID = ''
azureAPIKey = ''
azureRegion = ''
newAudio = ''
duration = ''
transcriptExists = False

# Custom tinker inicialization
app = customtkinter.CTk()
app.geometry("600x430")
app.title("TTSSTT")

def testBtn():
    newAudio = AudioSegment.from_wav(orgFilePath)
    duration = newAudio.duration_seconds
    fileHelper.seperateVoice(orgFilePath,duration)
    
# Start function 
def startBtn():
    global transcriptExists
    global errorMessages
    fileHelper.clearData() 
    print(langSettings)
    print(originalLang)
    print(orgFilePath)
    print(ytLink)
    print(serviceSTT)
    print(serviceTranslate)
    print(serviceTTS)
    print(googleCloudID)
    print(azureAPIKey)
    print(azureRegion)

    # UNCOMMENT LATER
    # if langSettings == {}:
    #     print('Brak języka')
    #     return
    # if orgFilePath == '' and ytLink == '':
    #     print('Brak linku/sciezki')
    #     return
    # if serviceSTT == '':
    #     print('brak stt')
    #     return
    # if serviceTranslate == '':
    #     print('brak translate')
    #     return
    # if serviceTTS == '':
    #     print('brak tts')
    #     return

    if(ytLink != ''):
        yt = YouTube('https://www.youtube.com/watch?v='+ytLink)
        duration = yt.length
        print(yt.length)
        transcriptExists = fileHelper.getTranscript(ytLink,langSettings,originalLang)

    fileExtension = pathlib.Path(orgFilePath).suffix
    print(fileExtension)
    # If fileExtension == mp4 or av, and some more
    # Run script to extract audio from video 
    if orgFilePath != '':
        if fileExtension != '.wav' and fileExtension != '.mp3':
            print('jestem')
            if fileHelper.audioFromVideo(orgFilePath):
                audiofilePath = 'files/audio.wav'
        else:
            audiofilePath = orgFilePath
        newAudio = AudioSegment.from_wav(audiofilePath)
        duration = newAudio.duration_seconds

    progressbar.set(0.2)
    # If fileExtension is alredy mp3 wav
    # Split audio to 1 min files when using google STT
    if (not transcriptExists):
        if serviceSTT == 'google':
            print(duration)
            print(audiofilePath)
            fileHelper.multipleSplit(1,duration,newAudio)
            newSTT.googleSTT(originalLang)
        if serviceSTT == 'azure':
            if azureAPIKey != '' and azureRegion != '':
                newSTT.azureSTT(originalLang, azureAPIKey)
            else:
                print("podaj klucz api oraz region")
                return
        if serviceSTT == 'google-cloud':
            if googleCloudID != '':
                newSTT.googleCloudSTT(originalLang,googleCloudID)
            else: 
                print("Podaj dane") 
                return
        progressbar.set(0.4)

        #Translate
        if serviceTranslate == 'google':
            Translate.googleTranslate(langSettings,serviceSTT)
        progressbar.set(0.6)
        if serviceTranslate == 'azure':
            if azureAPIKey != '' and azureRegion != '':
                Translate.azureTranslate(langSettings,azureAPIKey)
            else:
                print("podaj klucz api oraz region")
            return
        if serviceTranslate == 'deepL':
            Translate.deepLTranslate(langSettings)

    #TTS
    if serviceTTS == 'google':
        TTS.googleTTS(langSettings,serviceSTT,transcriptExists)
    progressbar.set(0.8)
    if serviceTTS == 'azure':
        if azureAPIKey != '' and azureRegion != '':
            TTS.azureTTS()
        else:
            print("podaj klucz api oraz region")
            return
    
    if serviceTTS == 'google' and not transcriptExists:
        fileHelper.margeAudio(langSettings)
    
    fileHelper.lenghtCheck(langSettings,duration)
    progressbar.set(1.0)

# Choose original language
def chooseOriginalLang(choice):
    global originalLang
    for lan in range(int(languageNums)):
        if choice == batchConfig[f'LANGUAGE-{lan}']['lang_name']:
            originalLang = batchConfig[f'LANGUAGE-{lan}']['synth_language_code']
# Select filepath
def selectFile():
    global orgFilePath
    fullFilePath = fd.askopenfile()
    orgFilePath = fullFilePath.name
    entryFilePath.insert(-1,fullFilePath.name)
# Select YT link
def takeYTLink():
    global ytLink
    ytLink = entryYTLink.get()


# Scrollable CheckBox list
class ScrollableCheckBoxFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, item_list, command=None, **kwargs):
        super().__init__(master, **kwargs)

        self.command = command
        self.checkbox_list = []
        for i, item in enumerate(item_list):
            self.addItem(item)

    def addItem(self, item):
        checkbox = customtkinter.CTkCheckBox(self, text=item)
        if self.command is not None:
            checkbox.configure(command=self.command)
        checkbox.grid(row=len(self.checkbox_list), column=0, pady=(0, 10))
        self.checkbox_list.append(checkbox)

    def removeItem(self, item):
        for checkbox in self.checkbox_list:
            if item == checkbox.cget("text"):
                checkbox.destroy()
                self.checkbox_list.remove(checkbox)
                return

    def getCheckedItems(self):
        return [checkbox.cget("text") for checkbox in self.checkbox_list if checkbox.get() == 1]

def checkboxFrameEvent():
    global langSettings
    langSettings.clear()
    for lan in range(int(languageNums)):
        for i in scrollable_checkbox_frame.getCheckedItems():
            if i==batchConfig[f'LANGUAGE-{lan}']['lang_name']:
                langSettings[lan]={
                    'translation_target_language': batchConfig[f'LANGUAGE-{lan}']['translation_target_language'],
                    'synth_language_code': batchConfig[f'LANGUAGE-{lan}']['synth_language_code'],
                    'synth_voice_name': batchConfig[f'LANGUAGE-{lan}']['synth_voice_name'],
                    'synth_voice_gender': batchConfig[f'LANGUAGE-{lan}']['synth_voice_gender']
                }

# Spacer
labelSpacer = customtkinter.CTkLabel(master=app, text="  ")
labelSpacer.grid(row=0,column=1)

# Choose file path
labelFile = customtkinter.CTkLabel(master=app, text="Choose file path (wideo.mp4 or audio.wav)")
labelFile.grid(row=0,column=0)
entryFilePath = customtkinter.CTkEntry(master=app ,placeholder_text='Choose path',width=300)
entryFilePath.grid(row=1,column=0)
btnFilePath = customtkinter.CTkButton(master=app, text="Choose", command=selectFile)
btnFilePath.grid(row=1,column=2)

# Choose YT Video link
labelYTLink = customtkinter.CTkLabel(master=app,text="Optional add YouTube video ID")
labelYTLink.grid(row=2,column=0)
entryYTLink = customtkinter.CTkEntry(master=app,placeholder_text=' https://www.youtube.com/watch?v=ID',width=300)
entryYTLink.grid(row=3,column=0)
btnYTLink = customtkinter.CTkButton(master=app, text="Save", command=takeYTLink)
btnYTLink.grid(row=3,column=2)

labelLangDef = customtkinter.CTkLabel(master=app,text="Choose original language:")
labelLangDef.grid(row=4,column=0,pady=5)
optionDefLang = customtkinter.CTkOptionMenu(master=app,values=[f"{langData['lang_name']}" for langNum, langData in batchSettings.items()],command=chooseOriginalLang)
optionDefLang.grid(row=4,column=2)

# Choose lang 
labelLang = customtkinter.CTkLabel(master=app,text="Choose which languages ​​to convert to:")
labelLang.grid(row=5,column=0)
scrollLang = customtkinter.CTkScrollableFrame(master=app,orientation='vertical')

# Scrollable Frame
scrollable_checkbox_frame = ScrollableCheckBoxFrame(master=app, width=200, command=checkboxFrameEvent,
                                                                 item_list=[f"{langData['lang_name']}" for langNum, langData in batchSettings.items()])
scrollable_checkbox_frame.grid(row=6, column=0)


progressbar = customtkinter.CTkProgressBar(app,width=500, height=15)
progressbar.grid(row=7, columnspan=5)
progressbar.set(0)

# Cloud config window
class CloudConfig(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x400")
        self.title("Cloud Config")
        # Select STT service function
        def radioBtnSTTEvent():
            global serviceSTT
            serviceSTT = lserviceSTT.get()

        def radioBtnTranslationEvent():
            global serviceTranslate
            serviceTranslate = lserviceTranslate.get()

        def radioBtnTTSEvent():
            global serviceTTS
            serviceTTS = lserviceTTS.get()

        def configConfirmBtn():
            global googleCloudID
            global azureAPIKey
            global azureRegion
            googleCloudID = self.entryGoogleProjectID.get()
            azureAPIKey = self.entryAzureRegion.get()
            azureRegion = self.entryAzureRegion.get()

        lserviceSTT = tkinter.StringVar(value='google')
        lserviceTranslate = tkinter.StringVar(value='google')
        lserviceTTS = tkinter.StringVar(value='google')
        #self.labelSpacer.grid(row=1,column=1)

        # Frame for STT service option
        self.radioBtnFrameSTT = customtkinter.CTkFrame(self, fg_color="transparent")
        # Radio button for STT service
        self.labelSTT = customtkinter.CTkLabel(self.radioBtnFrameSTT, text="Which STT service do you choose?")
        self.radioBtnSTTGoogle = customtkinter.CTkRadioButton(self.radioBtnFrameSTT, text="Google", command=radioBtnSTTEvent, variable=lserviceSTT, value='google')
        self.radioBtnSTTAzure = customtkinter.CTkRadioButton(self.radioBtnFrameSTT, text="Azure", command=radioBtnSTTEvent, variable=lserviceSTT, value='azure')
        self.radioBtnSTTGoogleCloud = customtkinter.CTkRadioButton(self.radioBtnFrameSTT, text="Google Cloud Platform", command=radioBtnSTTEvent, variable=lserviceSTT, value='google-cloud')
        # Positioning
        self.radioBtnFrameSTT.grid(row=1,column=1)
        self.labelSTT.grid(row=1, column=1)
        self.radioBtnSTTGoogle.grid(row=2,column=1)
        self.radioBtnSTTAzure.grid(row=2,column=2)
        self.radioBtnSTTGoogleCloud.grid(row=2,column=3)
        
        # Frame for Translation
        self.radioBtnFrameTranslation = customtkinter.CTkFrame(self, fg_color="transparent")
        # Radio button for Translate service
        self.labelTranslate = customtkinter.CTkLabel(self.radioBtnFrameTranslation, text="Which Translate service do you choose?")
        self.radioBtnTranslateGoogle = customtkinter.CTkRadioButton(self.radioBtnFrameTranslation, text="Google", command=radioBtnTranslationEvent, variable=lserviceTranslate, value='google')
        self.radioBtnTranslateAzure = customtkinter.CTkRadioButton(self.radioBtnFrameTranslation, text="Azure", command=radioBtnTranslationEvent, variable=lserviceTranslate, value='azure')
        self.radioBtnTranslateGoogleCloud = customtkinter.CTkRadioButton(self.radioBtnFrameTranslation, text="Google Cloud Platform", command=radioBtnTranslationEvent, variable=lserviceTranslate, value='google-cloud')
        # Positioning
        self.radioBtnFrameTranslation.grid(row=2,column=1)
        self.labelTranslate.grid(row=1, column=1)
        self.radioBtnTranslateGoogle.grid(row=2,column=1)
        self.radioBtnTranslateAzure.grid(row=2,column=2)
        self.radioBtnTranslateGoogleCloud.grid(row=2,column=3)

        # Frame for TTS
        self.radioBtnFrameTTS = customtkinter.CTkFrame(self, fg_color="transparent")
        # Radio button for TTS service
        self.labelTTS = customtkinter.CTkLabel(self.radioBtnFrameTTS, text="Which TTS service do you choose?")
        self.radioBtnTTSGoogle = customtkinter.CTkRadioButton(self.radioBtnFrameTTS, text="Google", command=radioBtnTTSEvent, variable=lserviceTTS, value='google')
        self.radioBtnTTSAzure = customtkinter.CTkRadioButton(self.radioBtnFrameTTS, text="Azure", command=radioBtnTTSEvent, variable=lserviceTTS, value='azure')
        self.radioBtnTTSGoogleCloud = customtkinter.CTkRadioButton(self.radioBtnFrameTTS, text="Google Cloud Platform", command=radioBtnTTSEvent, variable=lserviceTTS, value='google-cloud')
        # Positioning
        self.radioBtnFrameTTS.grid(row=3,column=1)
        self.labelTTS.grid(row=1, column=1)
        self.radioBtnTTSGoogle.grid(row=2,column=1)
        self.radioBtnTTSAzure.grid(row=2,column=2)
        self.radioBtnTTSGoogleCloud.grid(row=2,column=3)

        # Google Cloud platform project ID
        self.labelGoogleProjectID = customtkinter.CTkLabel(self, text="Enter the ID from the Google Cloud Project platform")
        self.entryGoogleProjectID = customtkinter.CTkEntry(self, placeholder_text='Enter your Google Cloud ID',width=300)
        self.labelGoogleProjectID.grid(row=5,column=1)
        self.entryGoogleProjectID.grid(row=6,column=1)
        # Azure API key 
        self.labelAzureAPI = customtkinter.CTkLabel(self, text="Enter the ID from the Azure platform")
        self.entryAzureAPI = customtkinter.CTkEntry(self, placeholder_text='Enter your Azure ID',width=300)
        self.labelAzureAPI.grid(row=7,column=1)
        self.entryAzureAPI.grid(row=8,column=1)
        # Azure region
        self.labelAzureRegion = customtkinter.CTkLabel(self, text="Provide a region from Azure")
        self.entryAzureRegion = customtkinter.CTkEntry(self, placeholder_text='Enter the Azure region',width=300)
        self.labelAzureRegion.grid(row=9,column=1)
        self.entryAzureRegion.grid(row=10,column=1)
        # Add button to accept and close window
        self.confirmSettBtn = customtkinter.CTkButton(self, text="Save", command=configConfirmBtn)
        self.confirmSettBtn.grid(row=11,column=2)


def openCloudConfig():
    global cloudConfig
    if cloudConfig is None or not cloudConfig.winfo_exists():
        cloudConfig = CloudConfig(app)
    else:
        cloudConfig.focus()

btnCloudConfig = customtkinter.CTkButton(master=app, text="Cloud Config", command=openCloudConfig)
btnCloudConfig.grid(row=6,column=3)



class ErrorMessage(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("500x120")
        self.title("Error")
        self.labelSTT = customtkinter.CTkLabel(self)
        self.labelSTT.grid()


# Check DeepL for translations and AssembleAI for Speech to Text

btnStart = customtkinter.CTkButton(master=app, text="Start", command=startBtn)
btnStart.grid(row=8,column=3)


btnStart = customtkinter.CTkButton(master=app, text="Test", command=testBtn)
btnStart.grid(row=9,column=3)

app.mainloop()