import PySimpleGUI as sg


def get_main_window():
    layout = [
        [
            sg.Text("Choose input PDF files: ", justification="right"),
            sg.Input(size=(50, 50), pad=1, disabled=True),
            sg.FilesBrowse(key="-IN-PDFS-", initial_folder="."),
        ],
        [
            sg.Text("Choose destination folder: ", justification="right"),
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
            sg.Button("RUN"),
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
        expand_x=True,
        expand_y=True,
    )
    layout = [
        [graph, sg.Text(key="-INFO-", size=(50, 1)), sg.OK(), sg.Exit()],
    ]
    window = sg.Window(
        "OCR", layout, finalize=True, resizable=True, return_keyboard_events=True
    )
    if img_data is not None:
        graph.draw_image(data=img_data, location=(0, 0))

    return window, graph
