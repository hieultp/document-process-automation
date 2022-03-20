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
        self.scale = 1

        # Rectangle drawing
        self.dragging = False
        self.start_point = self.end_point = None
        self.rect_id = None

        # Document visualizing
        self.img_data = None
        self.img_id = None
        self.img = None
        self.step = None

    def _resize_scroll_region(self, max_width, max_height):
        canvas = self.vizWindow["-COL-"].Widget.canvas
        # Configured the scroll region if the image is too big
        canvas.configure(scrollregion=(0, 0, max_width, max_height))

    def _resize_img(self, scale):
        self.graph.delete_figure(self.img_id)
        self.scale = scale
        self.processor.doc2img_scale = self.scale
        self.img, self.img_data = self.processor.get_doc_as_img(
            self.processor.current_doc
        )
        self._resize_scroll_region(
            max_width=self.img.width, max_height=self.img.height,
        )
        self.graph.set_size(
            size=(self.img.width, self.img.height)
        )  # resize the graph element to fit with new image size
        self.img_id = self.graph.draw_image(data=self.img_data, location=(0, 0))

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
        self.graph.set_size(size=(self.img.width, self.img.height))

    def _do_info_update(self):
        self.vizWindow["-INFO-"].update(
            value=f"Page {self.processor.current_doc * self.step + 1}/{self.total_pages}"
        )
        self.vizWindow["-OCR-STR-"].update(value=self.ocr_text)

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
        self.img, self.img_data = next(self.processor)
        self.vizWindow, self.graph, self.img_id = get_viz_window(
            self.processor.img.height,
            self.processor.img.width,
            self.img_data,
            self.icon,
        )
        self._resize_scroll_region(self.processor.img.width, self.processor.img.height)

        # Config the visualization window
        self.vizWindow["-OCR-STR-"].block_focus(block=True)
        self._do_info_update()

    def _handle_main_window_event(self, event, values):
        if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
            self._exit = True

        elif event == "RUN":
            # Errors handling
            # In case thang lon Dung khong select gi cả
            if values["-OUT-DIR-"] == "":
                sg.popup("Please select the destination folder", title="Notification")
                return
            if values["-IN-PDFS-"] == "":
                sg.popup(
                    "Please select the PDF files you need to split",
                    title="Notification",
                )
                return

            # Store the link to destination folder
            self.processor.dst_folder = Path(values["-OUT-DIR-"])
            self.step = 1 if values["-ONE-PAGE-"] else 3
            self.processor.add_documents(values["-IN-PDFS-"], self.step)
            self.total_pages = self.processor.total_docs * self.step

            self.mainWindow.hide()

            # Init visualization window
            self._init_viz_window()

    def _handle_viz_window_event(self, event, values):
        if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
            self._destroy_viz_window()

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
        elif event == "-ZOOM-IN-":
            self._resize_img(
                scale=min(self.scale + 0.5, 10)
            )  # increment 0.5, maximum zoom is 10 times
        elif event == "-ZOOM-OUT-":
            self._resize_img(
                scale=max(self.scale - 0.5, 1)
            )  # increment 0.5, minimum scale down to 1 times
        elif event in ("OK", "e",):  # "e,<Enter>" key will behave like an "OK" event
            if (
                event == "e"
                and self.vizWindow.FindElementWithFocus() == self.vizWindow["-OCR-STR-"]
            ):  # Handle case where event "e" is in the input box
                return

            self.processor.save_document(values["-OCR-STR-"])

            try:
                self.img, self.img_data = next(self.processor)
                self._viz_next_doc()
                self.ocr_text = self.processor.ocr(
                    *self.graph.get_bounding_box(self.rect_id)
                )
                self._do_info_update()
            except StopIteration:
                sg.popup(
                    "All files have been processed! Exit now...", title="Notification",
                )
                self._destroy_viz_window()

    def show(self):
        while not self._exit:
            window, event, values = sg.read_all_windows()
            if window == self.mainWindow:
                self._handle_main_window_event(event, values)
            if window == self.vizWindow:
                self._handle_viz_window_event(event, values)
