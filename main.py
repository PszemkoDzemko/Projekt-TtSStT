import PySimpleGUI as sg

sg.theme('Dark')

layout = [
    [sg.Text("Essa")],
    [sg.Text('File 1', size=(15, 1)),
    sg.InputText(key='-file1-'), sg.FileBrowse()],
    [sg.OK(), sg.Cancel()]
]

window = sg.Window("Essa", layout)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Cancel'):
        break

window.close()