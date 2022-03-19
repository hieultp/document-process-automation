import base64
from pathlib import Path

import PySimpleGUI as sg
from src.backend import Processor

from .main_window import get_main_window
from .viz_window import get_viz_window


class GUI:
    def __init__(self, processor: Processor) -> None:
        self.processor = processor

        # Prepare the UI
        self._init_app_icon()
        self.mainWindow = get_main_window(icon=self.icon)
        self.vizWindow = None

        self._exit = False

        # For visualization window
        self.graph: sg.Graph = None
        self.scroll_canvas: sg.Canvas = None
        self.total_pages = None
        self.ocr_text: str = ""

        # Rectangle drawing
        self.dragging = False
        self.start_point = self.end_point = None
        self.rect_id = None

        # Document visualizing
        self.img_data = None
        self.img_id = None
        self.step = None

    def _init_app_icon(self):
        # Hardcoded path of the icon
        with open("utils/icon.png", "rb") as icon_file:
            self.icon = base64.b64encode(icon_file.read())

    def _viz_next_doc(self):
        self.graph.delete_figure(self.img_id)  # Delete old image
        self.img_id = self.graph.draw_image(data=self.img_data, location=(0, 0))
        self.graph.send_figure_to_back(
            self.img_id
        )  # Send new image to the back so that the previous rectangle still shown

    def _do_info_update(self):
        current_page = self.processor.current_doc * self.step + 1
        self.vizWindow["-INFO-"].update(
            value=f"Page {current_page}/{self.total_pages} | Filename: "
        )
        self.vizWindow["-OCR-STR-"].update(value=self.ocr_text)

    def _save_document(self, filename):
        # Remove trailing empty spaces that might have
        # because of user input or bad OCR result
        filename = filename.strip()
        if filename == "":
            sg.popup_error(
                "Filename cannot be empty!", title="Filename Error", icon=self.icon
            )
            return False
        else:
            self.processor.save_document(filename)
            return True

    def _destroy_viz_window(self):
        self.vizWindow.close()
        self.vizWindow = None

        self.graph: sg.Graph = None
        self.scroll_canvas: sg.Canvas = None
        self.total_pages = None
        self.ocr_text: str = ""

        self.dragging = False
        self.start_point = self.end_point = None
        self.rect_id = None

        self.img_data = None
        self.img_id = None
        self.step = None

        self.mainWindow.un_hide()
        self.processor.reset()  # FIXME: Find a better way to handle this

    def _init_viz_window(self):
        self.img_data = next(self.processor)
        self.vizWindow, self.graph, self.img_id = get_viz_window(
            self.processor.img.height,
            self.processor.img.width,
            self.img_data,
            self.icon,
        )
        self.scroll_canvas = self.vizWindow["-COL-"].Widget.canvas

        # Config the visualization window
        self.vizWindow["-OCR-STR-"].block_focus(block=True)
        # Configured the scroll region if the image is too big
        self.scroll_canvas.configure(
            scrollregion=(0, 0, self.processor.img.width, self.processor.img.height)
        )
        self._do_info_update()

    def _handle_main_window_event(self, event, values):
        if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
            self._exit = True

        elif event == "Run":
            # Errors handling
            # In case thang lon Dung khong select gi cả
            if values["-IN-PDFS-"] == "":
                sg.popup_ok(
                    "Please select the PDF file(s) you need to split",
                    title="Notification",
                    icon=self.icon,
                )
                return
            if values["-OUT-DIR-"] == "":
                sg.popup_ok(
                    "Please select the destination folder to save processed the file(s)",
                    title="Notification",
                    icon=self.icon,
                )
                return

            # Store the link to destination folder
            self.processor.dst_folder = Path(values["-OUT-DIR-"])
            self.step = 1 if values["-ONE-PAGE-"] else 3
            self.processor.add_documents(values["-IN-PDFS-"], self.step)
            self.total_pages = self.processor.get_total_pages()

            # Init visualization window
            self.mainWindow.hide()
            self._init_viz_window()

    def _handle_viz_window_event(self, event, values):
        if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
            answer = sg.popup_yes_no(
                "Are you sure you want to quit?",
                title="Exit Confirmation",
                icon=self.icon,
            )
            if answer == "Yes":
                self._destroy_viz_window()

        elif event == "-GRAPH-":  # if there's a "Graph" event, then it's a mouse
            self.vizWindow["-OCR-STR-"].block_focus(block=True)
            x, y = values["-GRAPH-"]
            if not self.dragging:
                self.start_point = (x, y)
                self.dragging = True
            else:
                self.end_point = (x, y)
            if self.rect_id:
                self.graph.delete_figure(self.rect_id)
            if None not in (self.start_point, self.end_point):
                self.rect_id = self.graph.draw_rectangle(
                    self.start_point, self.end_point, line_color="red"
                )

        elif event.endswith("+UP"):  # The drawing has ended because mouse up
            self.ocr_text = self.processor.ocr(self.start_point, self.end_point)
            self._do_info_update()

            self.dragging = False
            self.start_point = self.end_point = None  # enable grabbing a new rect

        elif event in (
            "OK",
            "e",
        ):  # "e,<Enter>" key will behave like an "OK" event
            if (
                event == "e"
                and self.vizWindow.FindElementWithFocus() == self.vizWindow["-OCR-STR-"]
            ):  # Handle case where event "e" is in the input box
                return

            is_saved = self._save_document(values["-OCR-STR-"])
            if not is_saved:
                return
            try:
                self.img_data = next(self.processor)
                self._viz_next_doc()
                self.ocr_text = self.processor.ocr(
                    *self.graph.get_bounding_box(self.rect_id)
                )
                self._do_info_update()
            except StopIteration:
                sg.popup(
                    "All files have been processed! Exit now...",
                    title="Notification",
                )
                self._destroy_viz_window()

    def show(self):
        while not self._exit:
            window, event, values = sg.read_all_windows()
            if window == self.mainWindow:
                self._handle_main_window_event(event, values)
            if window == self.vizWindow:
                self._handle_viz_window_event(event, values)
