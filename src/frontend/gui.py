from pathlib import Path

import PySimpleGUI as sg
from src.backend import Processor

from .main_window import get_main_window
from .viz_window import get_viz_window


class GUI:
    def __init__(self, processor: Processor) -> None:
        self.processor = processor

        # Prepare the UI
        self.mainWindow = get_main_window()
        self.vizWindow = None
        self._exit = False

        # For visualization window
        self.graph: sg.Graph = None
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

    def _viz_next_doc(self):
        self.graph.delete_figure(self.img_id)  # Delete old image
        self.img_id = self.graph.draw_image(data=self.img_data, location=(0, 0))
        self.graph.send_figure_to_back(
            self.img_id
        )  # Send new image to the back so that the previous rectangle still shown

    def _do_info_update(self):
        self.vizWindow["-INFO-"].update(
            value=f"Page {self.processor.current_doc * self.step + 1}/{self.total_pages}"
        )
        self.vizWindow["-OCR-STR-"].update(value=self.ocr_text)

    def _handle_main_window_event(self, event, values):
        if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
            self._exit = True

        elif event == "RUN":
            # Errors handling
            # In case thang lon Dung khong select gi cả
            if values["-OUT-DIR-"] == "":
                sg.popup("Please select the destination folder", title="Notification")
            if values["-IN-PDFS-"] == "":
                sg.popup(
                    "Please select the PDF files you need to split",
                    title="Notification",
                )

            # Store the link to destination folder
            self.processor.dst_folder = Path(values["-OUT-DIR-"])
            self.step = 1 if values["-ONE-PAGE-"] else 3
            self.processor.add_documents(values["-IN-PDFS-"], self.step)
            self.total_pages = self.processor.total_docs * self.step

            self.mainWindow.hide()

            # Init visualization window
            self.img_data = next(self.processor)
            self.vizWindow, self.graph, self.img_id = get_viz_window(
                self.processor.img.height, self.processor.img.width, self.img_data
            )
            self.vizWindow["-OCR-STR-"].block_focus(block=True)
            self._do_info_update()

    def _handle_viz_window_event(self, event, values):
        if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
            self.vizWindow.close()
            self.vizWindow = None
            self.mainWindow.un_hide()

        if event == "-GRAPH-":  # if there's a "Graph" event, then it's a mouse
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

            self.processor.save_document(values["-OCR-STR-"])

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
                self.vizWindow.close()
                self.vizWindow = None
                self.mainWindow.un_hide()

    def show(self):
        while not self._exit:
            window, event, values = sg.read_all_windows()
            if window == self.mainWindow:
                self._handle_main_window_event(event, values)
            if window == self.vizWindow:
                self._handle_viz_window_event(event, values)