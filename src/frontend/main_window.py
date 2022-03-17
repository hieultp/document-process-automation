import PySimpleGUI as sg


def get_main_window(icon=None):
    layout = [
        [
            sg.Text(
                "Choose input PDF files: ", justification="left", pad=((22, 0), (0, 0))
            ),
            sg.Input(size=(50, 50), pad=1, disabled=True),
            sg.FileBrowse(key="-IN-PDFS-", initial_folder="."),
        ],
        [
            sg.Text("Choose destination folder: ", justification="left"),
            sg.Input(size=(50, 50), pad=1, disabled=True),
            sg.FolderBrowse(key="-OUT-DIR-", initial_folder="."),
        ],
        [
            sg.Radio(
                "Split 1 page per file", "RADIO1", default=False, key="-ONE-PAGE-"
            ),
            sg.Radio(
                "Split 3 pages per file", "RADIO1", default=True, key="-THREE-PAGES-"
            ),
            sg.Button("RUN", pad=((185, 0), (0, 0))),
            sg.Cancel(),
        ],
    ]
    return sg.Window(
        "DOCUMENTS PROCESS AUTOMATION - Version 0.0.0",
        layout,
        finalize=True,
        icon=icon,
    )
