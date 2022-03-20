import PySimpleGUI as sg


def get_viz_window(height=800, width=800, img_data=None, icon=None):
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
            sg.Button("Zoom In", size=(10, 1), key="-ZOOM-IN-"),
            sg.Button("Zoom Out", size=(10, 1), key="-ZOOM-OUT-"),
        ],
        [
            sg.Column(
                [[graph]],
                background_color="grey",
                scrollable=True,
                key="-COL-",
                size=(800, 900),
                expand_x= True,
                expand_y=True,
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
        icon=icon,
    )
    if img_data is not None:
        img_id = graph.draw_image(data=img_data, location=(0, 0))
    else:
        img_id = None

    return window, graph, img_id
