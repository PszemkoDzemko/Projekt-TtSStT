import tkinter
import configparser
import customtkinter
from tkinter import filedialog as fd

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")

# Variables
cloudConfig = None
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
filePath = ''
ytLink = ''
serviceSTT = ''
serviceTranslate = ''
serviceTTS = ''


# Custom tinker inicialization
app = customtkinter.CTk()
app.geometry("600x430")
app.title("TTSSTT")

# Start function 
def startBtn():
    print(serviceSTT)
    print(serviceTranslate)
    print(serviceTTS)
    if langSettings == {}:
        print('Brak języka')
        return
    if filePath == '' and ytLink == '':
        print('Brak linku/sciezki')
        return
    print(serviceSTT)
    if serviceSTT == '':
        print('brak stt')
        return
    if serviceTranslate == '':
        print('brak translate')
        return
    if serviceTTS == '':
        print('brak tts')
        return
    print('Button pressed')
    print(langSettings)
    print(originalLang)
    print(filePath)
    print(ytLink)

# Choose original language
def chooseOriginalLang(choice):
    global originalLang
    for lan in range(int(languageNums)):
        if choice == batchConfig[f'LANGUAGE-{lan}']['lang_name']:
            originalLang = batchConfig[f'LANGUAGE-{lan}']['synth_language_code']
# Select filepath
def selectFile():
    global filePath
    fullFilePath = fd.askopenfile()
    filePath = fullFilePath.name
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
labelFile = customtkinter.CTkLabel(master=app, text="Wybierz plik źródłowy (wideo.mp4 lub audio.wav)")
labelFile.grid(row=0,column=0)
entryFilePath = customtkinter.CTkEntry(master=app ,placeholder_text='Wybierz ścieżkę',width=300)
entryFilePath.grid(row=1,column=0)
buttonFilePath = customtkinter.CTkButton(master=app, text="Wybierz", command=selectFile)
buttonFilePath.grid(row=1,column=2)

# Choose YT Video link
labelYTLink = customtkinter.CTkLabel(master=app,text="Opcjonalnie podaj link do filmiku na Youtube.")
labelYTLink.grid(row=2,column=0)
entryYTLink = customtkinter.CTkEntry(master=app,placeholder_text='Podaj link do filmiku na YT',width=300)
entryYTLink.grid(row=3,column=0)
buttonYTLink = customtkinter.CTkButton(master=app, text="Zapisz", command=takeYTLink)
buttonYTLink.grid(row=3,column=2)

labelLangDef = customtkinter.CTkLabel(master=app,text="Wybierz oryginalny język:")
labelLangDef.grid(row=4,column=0,pady=5)
optionDefLang = customtkinter.CTkOptionMenu(master=app,values=[f"{langData['lang_name']}" for langNum, langData in batchSettings.items()],command=chooseOriginalLang)
optionDefLang.grid(row=4,column=2)

# Choose lang 
labelLang = customtkinter.CTkLabel(master=app,text="Wybierz na jakie języki przerobić:")
labelLang.grid(row=5,column=0)
scrollLang = customtkinter.CTkScrollableFrame(master=app,orientation='vertical')

# Scrollable Frame
scrollable_checkbox_frame = ScrollableCheckBoxFrame(master=app, width=200, command=checkboxFrameEvent,
                                                                 item_list=[f"{langData['lang_name']}" for langNum, langData in batchSettings.items()])
scrollable_checkbox_frame.grid(row=6, column=0)


# Cloud config window
class CloudConfig(customtkinter.CTkToplevel):
    global serviceSTT
    global serviceTranslate
    global serviceTTS
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x300")
        self.title("Cloud Config")
        # Select STT service function
        def radioBtnSTTEvent():
            serviceSTT = lserviceSTT.get()
            print("STT toggled, current value:", serviceSTT)

        def radioBtnTranslationEvent():
            serviceTranslate = lserviceTranslate.get()
            print("Translate toggled, current value:", serviceTranslate)

        def radioBtnTTSEvent():
            serviceTTS = lserviceTTS.get()
            print("TTS toggled, current value:", serviceTTS)


        lserviceSTT = tkinter.StringVar(value='google')
        lserviceTranslate = tkinter.StringVar(value='google')
        lserviceTTS = tkinter.StringVar(value='google')
        #self.labelSpacer.grid(row=1,column=1)

        # Frame for STT service option
        self.radioBtnFrameSTT = customtkinter.CTkFrame(self)
        # Radio button for STT service
        self.labelSTT = customtkinter.CTkLabel(self.radioBtnFrameSTT, text="Jaką usługę STT wybierasz?")
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
        self.radioBtnFrameTranslation = customtkinter.CTkFrame(self)
        # Radio button for Translate service
        self.labelTranslate = customtkinter.CTkLabel(self.radioBtnFrameTranslation, text="Jaką usługę Translate wybierasz?")
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
        self.radioBtnFrameTTS = customtkinter.CTkFrame(self)
        # Radio button for TTS service
        self.labelTTS = customtkinter.CTkLabel(self.radioBtnFrameTTS, text="Jaką usługę TTS wybierasz?")
        self.radioBtnTTSGoogle = customtkinter.CTkRadioButton(self.radioBtnFrameTTS, text="Google", command=radioBtnTTSEvent, variable=lserviceTTS, value='google')
        self.radioBtnTTSAzure = customtkinter.CTkRadioButton(self.radioBtnFrameTTS, text="Azure", command=radioBtnTTSEvent, variable=lserviceTTS, value='azure')
        self.radioBtnTTSGoogleCloud = customtkinter.CTkRadioButton(self.radioBtnFrameTTS, text="Google Cloud Platform", command=radioBtnTTSEvent, variable=lserviceTTS, value='google-cloud')
        # Positioning
        self.radioBtnFrameTTS.grid(row=3,column=1)
        self.labelTTS.grid(row=1, column=1)
        self.radioBtnTTSGoogle.grid(row=2,column=1)
        self.radioBtnTTSAzure.grid(row=2,column=2)
        self.radioBtnTTSGoogleCloud.grid(row=2,column=3)

        # Add input fields for cloud config
        # Google Cloud platform project ID
        # Azure API key 
        # Azure region
        # Add button to accept and close window



def openCloudConfig():
    global cloudConfig
    if cloudConfig is None or not cloudConfig.winfo_exists():
        cloudConfig = CloudConfig(app)
        cloudConfig.focus()
    else:
        cloudConfig.focus()

buttonCloudConfig = customtkinter.CTkButton(master=app, text="Cloud Config", command=openCloudConfig)
buttonCloudConfig.grid(row=6,column=3)


# Add if in start button check that all cloud services are selected
# Add progress bar 
# Split STT.py to seperate files like STT TTS Translate or even more 
# Check DeepL for translations and AssembleAI for Speech to Text


buttonStart = customtkinter.CTkButton(master=app, text="Start", command=startBtn)
buttonStart.grid(row=7,column=3)


app.mainloop()