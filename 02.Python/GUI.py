import PySimpleGUI as sg

############################## CREATE UI ###########################################
sg.theme("LightGrey1")
layout = [[sg.Text(text="Choose destination folder: ",
                   justification="right",
                   size=(20, 1)),
           sg.Input(size=(50, 50),
                    pad=1, disabled=True),
           sg.FolderBrowse(key="-IN-",
                           size=(10, 1))],
          [sg.Text("Choose input PDF files: ",
                   justification="right",
                   size=(20, 1)),
              sg.Input(size=(50, 50),
                       pad=1, disabled=True),
              sg.FilesBrowse(key="-IN1-",
                             size=(10, 1))],
          [sg.Button("RUN",
                     size=(10, 1),
                     pad=((426, 10), (2, 2))),
           sg.Button("Cancel",
           size=(10, 1),
              pad=((10, 10), (2, 2)))]]

window = sg.Window("DOCUMENTS PROCESS AUTOMATION", layout, size=(650, 110))

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Cancel":
        break
    elif event == "RUN":
        destination_folder = values["-IN-"] #store the link to destination folder
        PDF_files = values["-IN1-"] #stored the input PDF files
window.close()
