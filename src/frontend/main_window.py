import PySimpleGUI as sg


def get_main_window(icon=None):
    layout = [
        [
            sg.Text(
                "Choose input PDF file(s): ",
                justification="left",
                pad=((15, 0), (0, 0)),
            ),
            sg.Input(size=(50, 50), pad=1, disabled=True),
            sg.FilesBrowse(
                key="-IN-PDFS-",
                initial_folder=".",
                file_types=(("PDF File(s)", "*.pdf"),),
            ),
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
        "DOCUMENTS PROCESS AUTOMATION - Version 1.0.0",
        layout,
        finalize=True,
        icon=icon,
    )
