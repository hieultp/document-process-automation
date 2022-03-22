import base64
from pathlib import Path

import PySimpleGUI as sg
from src.backend import Processor

from .main_window import get_main_window
from .viz_window import get_viz_window
from .support_window import get_popup_window
from .support_window import program_information
from.support_window import developers_information


class GUI:
    def __init__(self, processor: Processor) -> None:
        self.processor = processor

        # Prepare the UI
        self._init_app_icon()
        self.mainWindow = get_main_window()
        self.vizWindow = None
        self.popupWindow = None

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
        self.img_id = None
        self.step = None

    def _resize_scroll_region(self, max_width, max_height):
        canvas = self.vizWindow["-COL-"].Widget.canvas
        # Configured the scroll region if the image is too big
        canvas.configure(scrollregion=(0, 0, max_width, max_height))

    def _resize_img(self, scale):
        # Get/update new image and scale value
        img, img_data = self.processor.get_doc_as_img(
            self.processor.current_doc, scale=scale
        )
        self.processor.doc2img_scale = scale
        self.processor.img = img

        self._resize_scroll_region(
            max_width=img.width, max_height=img.height,
        )
        self._viz_doc(img_data)

    def _init_app_icon(self):
        # Hardcoded path of the icon
        with open("utils/icon.png", "rb") as icon_file:
            icon = base64.b64encode(icon_file.read())
        sg.set_global_icon(icon)

    def _viz_doc(self, img_data):
        self.graph.delete_figure(self.img_id)  # Delete old image
        self.img_id = self.graph.draw_image(data=img_data, location=(0, 0))
        self.graph.send_figure_to_back(
            self.img_id
        )  # Send new image to the back so that the previous rectangle still shown
        img_width = self.processor.img.width
        img_height = self.processor.img.height
        self.graph.set_size(size=(img_width, img_height))
        self.graph.change_coordinates(
            graph_bottom_left=(0, img_height), graph_top_right=(img_width, 0)
        )

    def _do_info_update(self):
        self.vizWindow["-INFO-"].update(
            value=f"Page {self.processor.current_page}/{self.total_pages} | Filename: "
        )
        self.vizWindow["-OCR-STR-"].update(value=self.ocr_text)

    def _save_document(self, filename):
        # Remove trailing empty spaces that might have
        # because of user input or bad OCR result
        # FIXME: find a better way for looping character in special_character
        special_character = ["\\", "/", ":", "*", "?", "|", "<", ">"]
        filename = filename.strip()
        for character in special_character:
            if character in filename:
                answer = self._init_popup_notification(
                    "Filename cannot contain special character:\n" + character,
                    title="Error",
                    type="OK",
                )
                if answer:
                    self._clear_popup_notification()
                    return False
        if filename == "":
            answer = self._init_popup_notification(
                "Filename cannot be empty!", title="Error", type="OK"
            )
            if answer:
                self._clear_popup_notification()
                return False
        else:
            self.processor.save_document(filename)
            return True

    def _destroy_viz_window(self):
        self.vizWindow.close()
        self.popupWindow.close()
        self.vizWindow = None
        self.popupWindow = None

        self.graph: sg.Graph = None
        self.total_pages = None
        self.ocr_text: str = ""

        self.dragging = False
        self.start_point = self.end_point = None
        self.rect_id = None

        self.img_id = None

        self.mainWindow.un_hide()
        self.processor.reset()  # FIXME: Find a better way to handle this

    def _fit_img(self, img_width):
        col_width = self.vizWindow["-COL-"].get_size()[0]
        init_scale = self.processor.doc2img_scale
        scale_x = col_width // (
            img_width / init_scale
        )  # The image height will be automatically adjust follow the width
        self._resize_img(scale_x)

    def _init_viz_window(self):
        img_data = self.processor.next_doc()
        self.vizWindow, self.graph, self.img_id = get_viz_window(
            self.processor.img.height, self.processor.img.width, img_data,
        )

        # Config the visualization window
        self.vizWindow["-OCR-STR-"].block_focus(block=True)
        self._do_info_update()
        self.vizWindow.Maximize()  # FIXME: Maximize windoww - use for row 167

    def _init_popup_notification(self, text, title, type=None):
        self.popupWindow = get_popup_window(text=text, title=title, type=type)
        user_answers = self.popupWindow.read()[0]
        return user_answers

    def _clear_popup_notification(self):
        self.popupWindow.close()
        self.popupWindow = None
    def _handle_menu_bar_event(self,event):
        if event == "About":
            answer = self._init_popup_notification(
                program_information(), title="DOPA", type="OK"
                )
            if answer:
                self._clear_popup_notification()
                return
        elif event == "Manual":
            answer = self._init_popup_notification(
                "This program is easy to use, no need for manual", title="DOPA", type="OK"
                )
            if answer:
                self._clear_popup_notification()
                return
        elif event == "Contacts":
            answer = self._init_popup_notification(developers_information()
                , title="Contacts", type="OK"
                )
            if answer:
                self._clear_popup_notification()
                return
    def _handle_main_window_event(self, event, values):
        if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
            self._exit = True
        elif event in ("About","Manual","Contacts"):
            self._handle_menu_bar_event(event=event)
        elif event == "Run":
            # Errors handling
            # In case thang lon Dung khong select gi cả
            if values["-IN-PDFS-"] == "":
                answer = self._init_popup_notification(
                    "Please select the PDF file(s) you need to split",
                    title="Notification",
                    type="OK",
                )
                if answer:
                    self._clear_popup_notification()
                    return
            if values["-OUT-DIR-"] == "":
                answer = self._init_popup_notification(
                    "Please select the destination folder to save processed file(s)",
                    title="Notification",
                    type="OK",
                )
                if answer:
                    self._clear_popup_notification()
                    return

            # Store the link to destination folder
            pages_per_doc = 1 if values["-ONE-PAGE-"] else 3
            self.processor.dst_folder = Path(values["-OUT-DIR-"])
            self.processor.add_documents(values["-IN-PDFS-"], pages_per_doc)
            self.total_pages = self.processor.get_total_pages()

            # Init visualization window
            self.mainWindow.hide()
            self._init_viz_window()
            self.vizWindow.finalize()
            self._fit_img(
                self.processor.img.width
            )  # FIXME: Did not work, because the program did not take the new column width after maximize

    def _handle_viz_window_event(self, event, values):
        if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
            answer = self._init_popup_notification(
                "Are you sure you want to exit?", title="Exit",
            )
            if answer == "-OK-":
                self._destroy_viz_window()
            else:
                self._clear_popup_notification()

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

        elif (
            event in ("e", "q")
            and self.vizWindow.FindElementWithFocus() == self.vizWindow["-OCR-STR-"]
        ):  # Handle case where predefined keyboard event is in the input box
            return
        elif event == "-FIT-":
            self._fit_img(self.processor.img.width)

        if "ZOOM" in event:
            if "IN" in event:
                # Increment 0.5, maximum zoom is 10 times
                scale = min(self.processor.doc2img_scale + 0.5, 10.0)
            elif "OUT" in event:  # Zoom out
                # Decrement 0.5, minimum scale down to 1 times
                scale = max(self.processor.doc2img_scale - 0.5, 1.0)
            else:
                col_height = self.vizWindow["-COL-"].get_size()[1]
                scale = col_height / (
                    self.processor.img.height / self.processor.doc2img_scale
                )
            self._resize_img(scale)

        elif event in ("Next", "e"):
            is_saved = self._save_document(values["-OCR-STR-"])
            if not is_saved:
                return

            img_data = self.processor.next_doc()
            if img_data is not None:
                self._viz_doc(img_data)
                if self.rect_id:
                    # Do this step if we have the info of the previous selected region
                    self.ocr_text = self.processor.ocr(
                        *self.graph.get_bounding_box(self.rect_id)
                    )
                else:
                    self.ocr_text = ""
                self._do_info_update()
            else:
                self._init_popup_notification(
                    "All files have been processed! Exit now...",
                    title="Notification",
                    type="OK",
                )
                self._destroy_viz_window()

        elif event in ("Previous", "q"):
            if self.processor.processed_filenames:
                answer = self._init_popup_notification(
                    "Are you sure you want to go back to the previous page?\nThis will delete all processed files belong to the prior page.",
                    title="Exit Confirmation",
                )
                if answer != "-OK-":
                    self._clear_popup_notification()
                    return
                self._clear_popup_notification()
                prev_filename = self.processor.delete_prev_saved_doc()
                img_data = self.processor.previous_doc()
                if img_data is not None:
                    self._viz_doc(img_data)
                    self.ocr_text = prev_filename
                    self._do_info_update()

    def show(self):
        while not self._exit:
            window, event, values = sg.read_all_windows()
            if window == self.mainWindow:
                self._handle_main_window_event(event, values)
            if window == self.vizWindow:
                self._handle_viz_window_event(event, values)
