import PySimpleGUI as sg


def developers_information():
    developer = "Phuoc Hieu Le\n"
    email = "hieultp1@gmail.com\n"
    git_acc = "https://hieultp.github.io/                    " + "\n" #Cheating on size window =))))

    text = f"{developer}{email}{git_acc}"
    return text


def program_information():
    headlines = "Document Process Automation (DOPA)\n"
    version = "Version: 2.0.0\n"
    date_issue = "Date Issue: MM/DD/YYYY\n"

    text = f"{headlines}{version}{date_issue}"
    return text


def menu_bar():
    menu_def = [["&Help", ["&Manual", "&About", "&Contacts"]]]
    layout = sg.Menu(menu_def, pad=((0, 0), (0, 0)), background_color=None)
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
