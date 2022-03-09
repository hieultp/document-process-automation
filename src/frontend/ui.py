import PySimpleGUI as sg


def get_main_window():
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
    return sg.Window("DOCUMENTS PROCESS AUTOMATION", layout, finalize=True)


def get_viz_window(height=800, width=800, img_data=None):
    graph = sg.Graph(
        canvas_size=(width, height),
        graph_bottom_left=(0, height),
        graph_top_right=(width, 0),
        background_color="lightblue",
        key="-GRAPH-",
        enable_events=True,  # mouse click events
        drag_submits=True,
        expand_x=False,
        expand_y=False,
    )
    layout = [
        [
            sg.Text(key="-INFO-", size=(10, 1)),
            sg.Input(key="-OCR-STR-", size=(20, 1)),
        ],
        [
            sg.OK(size=(10, 1), bind_return_key=True),
            sg.Exit(size=(10, 1)),
        ],
        [graph],
    ]
    window = sg.Window(
        "OCR",
        layout,
        finalize=True,
        resizable=True,
        return_keyboard_events=True,
        element_justification="center",
    )
    if img_data is not None:
        graph.draw_image(data=img_data, location=(0, 0))

    return window, graph
