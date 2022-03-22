import PySimpleGUI as sg
from .support_window import menu_bar


def get_main_window():
    layout = [
        [menu_bar()],
        [
            sg.Text(
                "Choose input PDF file(s): ",
                justification="left",
                pad=((15, 0), (0, 0)),
            ),
            sg.Input(
                size=(50, 50),
                pad=((1, 0), (0, 0)),
                disabled=True,
                background_color="#DAE0E6",
            ),
            sg.FilesBrowse(
                key="-IN-PDFS-",
                initial_folder=".",
                file_types=(("PDF File(s)", "*.pdf"),),
                tooltip="Locate input files",
            ),
        ],
        [
            sg.Text("Choose destination folder: ", justification="left"),
            sg.Input(
                size=(50, 50),
                pad=((1, 0), (0, 0)),
                disabled=True,
                background_color="#DAE0E6",
            ),
            sg.FolderBrowse(
                key="-OUT-DIR-", initial_folder=".", tooltip="Locate output folder"
            ),
        ],
        [
            sg.Radio(
                "Split 1 page per file", "RADIO1", default=False, key="-ONE-PAGE-"
            ),
            sg.Radio(
                "Split 3 pages per file", "RADIO1", default=True, key="-THREE-PAGES-"
            ),
            sg.Button("Run", pad=((190, 0), (1, 1)), tooltip="Run"),
            sg.Cancel(tooltip="Exit application", pad=((5, 0), (1, 1))),
        ],
    ]
    return sg.Window("DOCUMENTS PROCESS AUTOMATION", layout, finalize=True)
