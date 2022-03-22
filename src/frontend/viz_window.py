import PySimpleGUI as sg


def get_popup_window(text, title="Notification"):
    noti_layout = [
        [sg.Text(text=text)],
        [sg.OK(key="-OK-"), sg.Button("Cancel", key="-CANCEL-"),],
    ]
    noti_window = sg.Window(
        title=title,
        layout=noti_layout,
        finalize=True,
        resizable=False,
        element_justification="center",
    )
    return noti_window


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
            sg.Button("Previous", size=(10, 1)),
            sg.Button("Next", size=(10, 1), bind_return_key=True),
            sg.Exit(size=(10, 1)),
            sg.Button("Zoom In", size=(10, 1), key="-ZOOM-IN-"),
            sg.Button("Zoom Out", size=(10, 1), key="-ZOOM-OUT-"),
            sg.Button("Fit to page", size=(10, 1), key="-ZOOM-NORMAL-"),
            sg.Button("Fit to width", size=(10, 1), key="-FIT-"),
        ],
        [
            sg.Text(key="-INFO-", size=(18, 1), justification="right"),
            sg.Input(key="-OCR-STR-", size=(20, 1)),
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Column(
                [[graph]],
                background_color="grey",
                scrollable=True,
                key="-COL-",
                expand_x=True,
                expand_y=True,
                element_justification="c",
            )
        ],
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
        img_id = graph.draw_image(data=img_data, location=(0, 0))
    else:
        img_id = None

    return window, graph, img_id
