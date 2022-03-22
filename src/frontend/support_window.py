import PySimpleGUI as sg


def menu_bar():
    menu_def = [["Help"], ["About"]]
    layout = sg.Menu(menu_def, pad=((5,0),(1,1)))
    return layout


def get_popup_window(text, title="Notification", type=None):
    if type == None:
        cancel_visibility = True
    else:
        cancel_visibility = False
    noti_layout = [
        [sg.Text(text=text)],
        [
            sg.OK(key="-OK-", size=(10, 1)),
            sg.Button(
                "Cancel", size=(10, 1), key="-CANCEL-", visible=cancel_visibility
            ),
        ],
    ]
    noti_window = sg.Window(
        title=title,
        layout=noti_layout,
        finalize=True,
        resizable=False,
        element_justification="center",
    )
    return noti_window
