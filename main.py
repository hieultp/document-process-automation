from pathlib import Path
from typing import List, Tuple

import numpy as np
import PySimpleGUI as sg
from fitz import Document, Matrix, Pixmap
from paddleocr import PaddleOCR
from PIL import Image

from src.backend.pdf_processing import save_pdf, split_pdf
from src.frontend.ui import get_main_window, get_viz_window

sg.theme("LightGrey1")
sg.set_options(dpi_awareness=True)


def get_page_as_img(pdf_file: Document):
    pix: Pixmap = pdf_file.load_page(page_id=0).get_pixmap(matrix=Matrix(2.0, 2.0))
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return img, pix.tobytes("ppm")


def viz_next_doc(
    graph: sg.Graph, pdf_files: List[Document], current_doc: int, img_id: int
):
    current_doc += 1
    graph.delete_figure(img_id)
    page_as_img, img_data = get_page_as_img(pdf_files[current_doc])
    img_id = graph.draw_image(data=img_data, location=(0, 0))
    graph.send_figure_to_back(img_id)
    return page_as_img, current_doc, img_id


def do_ocr(
    ocr: PaddleOCR,
    img: Image.Image,
    start_point: Tuple[int, int],
    end_point: Tuple[int, int],
):
    if start_point is None or end_point is None:
        return None

    x1, y1 = start_point
    x2, y2 = end_point
    if x1 == x2 or y1 == y2:
        return None
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1

    crop = img.crop((x1, y1, x2, y2))
    text = ocr.ocr(np.asarray(crop), det=False)
    return text[0][0] if text else None


def do_info_update(window, current_doc, total_files, step=1, ocr_text=None):
    window["-INFO-"].update(value=f"Page {current_doc * step + 1}/{total_files * step}")
    window["-OCR-STR-"].update(value=text if ocr_text is not None else "")


if __name__ == "__main__":
    # Prepare the OCR model
    BASE_MODEL_PATH = Path(".paddleocr/2.4/ocr")
    BASE_PPOCR_UTILS_PATH = Path(".paddleocr/ppocr/utils")
    ocr = PaddleOCR(
        cls_model_dir=str(BASE_MODEL_PATH / "cls/ch_ppocr_mobile_v2.0_cls_infer"),
        det_model_dir=str(BASE_MODEL_PATH / "det/en/en_ppocr_mobile_v2.0_det_infer"),
        rec_model_dir=str(BASE_MODEL_PATH / "rec/en/en_number_mobile_v2.0_rec_infer"),
        e2e_char_dict_path=str(BASE_PPOCR_UTILS_PATH / "ic15_dict.txt"),
        rec_char_dict_path=str(BASE_PPOCR_UTILS_PATH / "en_dict.txt"),
        use_gpu=False,
        use_angle_cls=True,
        lang="en",
        warmup=True,
    )

    # Prepare the UI
    mainWindow = get_main_window()
    vizWindow = None

    # For visualization window
    graph = None
    dragging = False
    start_point = end_point = prior_rect = None

    destination_folder = None
    pdf_filepaths = None
    pdf_files = None
    current_doc = 0
    page_as_img = None
    img_id = None
    step = None
    filename = None

    while True:
        window, event, values = sg.read_all_windows()

        if window == mainWindow:
            if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
                break

            elif event == "RUN":
                # Errors handling
                # In case thang lon Dung khong select gi cả
                if values["-OUT-DIR-"] == "":
                    sg.popup(
                        "Please select the destination folder", title="Notification"
                    )
                    break
                if values["-IN-PDFS-"] == "":
                    sg.popup(
                        "Please select the PDF files you need to split",
                        title="Notification",
                    )
                    break

                # Store the link to destination folder
                destination_folder = Path(values["-OUT-DIR-"])
                pdf_filepaths = values["-IN-PDFS-"]
                step = 1 if values["-ONE-PAGE-"] else 3
                pdf_files: List[Document] = split_pdf(pdf_filepaths, step=step)

                mainWindow.hide()

                # Init visualization window
                page_as_img, img_data = get_page_as_img(pdf_files[current_doc])
                vizWindow, graph, img_id = get_viz_window(
                    page_as_img.height, page_as_img.width, img_data
                )
                vizWindow["-OCR-STR-"].block_focus(block=True)
                do_info_update(vizWindow, current_doc, len(pdf_files), step)

        if window == vizWindow:
            canvas = vizWindow["-COL-"].Widget.canvas
            # Configured the scroll region if the image is too big
            canvas.configure(scrollregion=(0, 0, page_as_img.width, page_as_img.height))
            if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
                vizWindow.close()
                vizWindow = None
                mainWindow.un_hide()

            if event == "-GRAPH-":  # if there's a "Graph" event, then it's a mouse
                vizWindow["-OCR-STR-"].block_focus(block=True)
                x, y = values["-GRAPH-"]
                if not dragging:
                    start_point = (x, y)
                    dragging = True
                else:
                    end_point = (x, y)
                if prior_rect:
                    graph.delete_figure(prior_rect)
                if None not in (start_point, end_point):
                    prior_rect = graph.draw_rectangle(
                        start_point, end_point, line_color="red"
                    )
            elif event.endswith("+UP"):  # The drawing has ended because mouse up
                info = window["-INFO-"]
                ocr_str = window["-OCR-STR-"]

                text = do_ocr(ocr, page_as_img, start_point, end_point)
                do_info_update(window, current_doc, len(pdf_files), step, ocr_text=text)

                dragging = False
                start_point = end_point = None
            elif event in ("OK", "e"):  # "e,<Enter>" key will behave like an "OK" event
                if (
                    event == "e"
                    and window.FindElementWithFocus() == window["-OCR-STR-"]
                ):  # Handle case where event "e" is in the input box
                    continue

                pdf_name = values["-OCR-STR-"]
                save_pdf(pdf_files[current_doc], destination_folder / f"{pdf_name}.pdf")

                if current_doc + 1 < len(pdf_files):
                    page_as_img, current_doc, img_id = viz_next_doc(
                        graph, pdf_files, current_doc, img_id
                    )
                    start_point, end_point = graph.get_bounding_box(prior_rect)
                    text = do_ocr(ocr, page_as_img, start_point, end_point)
                    do_info_update(
                        window, current_doc, len(pdf_files), step, ocr_text=text
                    )
                    start_point, end_point = None, None  # enable grabbing a new rect
                else:
                    sg.popup(
                        "All files have been processed! Exit now...",
                        title="Notification",
                    )
                    vizWindow.close()
                    vizWindow = None
                    mainWindow.un_hide()
