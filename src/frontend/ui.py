import PySimpleGUI as sg


def get_main_window():
    layout = [
        [
            sg.Text("Choose input PDF files: ", justification="right", size=(20, 1)),
            sg.Input(size=(50, 50), pad=1, disabled=True),
            sg.FilesBrowse(key="-IN-PDFS-", size=(10, 1)),
        ],
        [
            sg.Text(
                text="Choose destination folder: ", justification="right", size=(20, 1)
            ),
            sg.Input(size=(50, 50), pad=1, disabled=True),
            sg.FolderBrowse(key="-OUT-DIR-", size=(10, 1)),
        ],
        [
            sg.Radio(
                "Split 1 page per file", "RADIO1", default=False, key="-ONE-PAGE-"
            ),
            sg.Radio(
                "Split 3 pages per file", "RADIO1", default=True, key="-THREE-PAGES-"
            ),
            sg.Button("RUN", size=(10, 1)),
            sg.Cancel(size=(10, 1)),
        ],
    ]
    return sg.Window(
        "DOCUMENTS PROCESS AUTOMATION", layout, size=(650, 110), finalize=True
    )


def get_viz_window(height=800, width=800):
    graph = sg.Graph(
        canvas_size=(width, height),
        graph_bottom_left=(0, height),
        graph_top_right=(width, 0),
        background_color="lightblue",
        key="-GRAPH-",
        enable_events=True,  # mouse click events
        drag_submits=True,
        expand_x=True,
        expand_y=True,
    )
    layout = [
        [graph, sg.Text(key="info", size=(60, 1)), sg.OK(), sg.Exit()],
    ]

    return (
        sg.Window(
            "OCR", layout, finalize=True, resizable=True, return_keyboard_events=True
        ),
        graph,
    )
