import tkinter
import configparser
import customtkinter
from tkinter import filedialog as fd

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")

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
# Comment
app = customtkinter.CTk()
app.geometry("600x430")
app.title("TTSSTT")

def button_function():
    print('Button pressed')
    print(langSettings)
    print(originalLang)
    print(filePath.name)
    print(ytLink)

# Choose original language
def chooseOriginalLang(choice):
    global originalLang
    for lan in range(int(languageNums)):
        if choice == batchConfig[f'LANGUAGE-{lan}']['lang_name']:
            originalLang = batchConfig[f'LANGUAGE-{lan}']['synth_language_code']

def selectFile():
    global filePath
    filePath = fd.askopenfile()
    entryFilePath.insert(-1,filePath.name)

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
            self.add_item(item)

    def add_item(self, item):
        checkbox = customtkinter.CTkCheckBox(self, text=item)
        if self.command is not None:
            checkbox.configure(command=self.command)
        checkbox.grid(row=len(self.checkbox_list), column=0, pady=(0, 10))
        self.checkbox_list.append(checkbox)

    def remove_item(self, item):
        for checkbox in self.checkbox_list:
            if item == checkbox.cget("text"):
                checkbox.destroy()
                self.checkbox_list.remove(checkbox)
                return

    def get_checked_items(self):
        return [checkbox.cget("text") for checkbox in self.checkbox_list if checkbox.get() == 1]

def checkbox_frame_event():
    global langSettings
    langSettings.clear()
    for lan in range(int(languageNums)):
        for i in scrollable_checkbox_frame.get_checked_items():
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
scrollable_checkbox_frame = ScrollableCheckBoxFrame(master=app, width=200, command=checkbox_frame_event,
                                                                 item_list=[f"{langData['lang_name']}" for langNum, langData in batchSettings.items()])
scrollable_checkbox_frame.grid(row=6, column=0)

buttonStart = customtkinter.CTkButton(master=app, text="Start", command=button_function)
buttonStart.grid(row=7,column=3)



app.mainloop()