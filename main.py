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

TMP_DIR = Path(".tmp/")


def rm_files(pth: Path):
    for child in pth.glob("*"):
        if child.is_file():
            child.unlink()


def init_tmp_dir():
    try:
        TMP_DIR.mkdir()
    except FileExistsError:
        rm_files(TMP_DIR)


def clean_tmp_dir(page_as_img: Image.Image):
    page_as_img.close()
    rm_files(TMP_DIR)


def get_page_as_img(pdf_file: Document):
    pix: Pixmap = pdf_file.load_page(page_id=0).get_pixmap(matrix=Matrix(2.0, 2.0))
    pix.save(TMP_DIR / "tmp.png")
    img = Image.open(TMP_DIR / "tmp.png")
    return img, pix.tobytes(), pix.height, pix.width


def viz_next_doc(graph: sg.Graph, pdf_files: List[Document], current_doc: int):
    current_doc += 1
    graph.erase()
    page_as_img, img_data, _, _ = get_page_as_img(pdf_files[current_doc])
    graph.draw_image(data=img_data, location=(0, 0))
    return page_as_img, current_doc


def do_ocr(
    ocr: PaddleOCR,
    img: Image.Image,
    start_point: Tuple[int, int],
    end_point: Tuple[int, int],
):
    # TODO: Handle different cases with start_point, end_point
    if start_point is None or end_point is None:
        return None

    crop = img.crop((*start_point, *end_point))
    text = ocr.ocr(np.asarray(crop), det=False)
    return text[0][0] if text else None


if __name__ == "__main__":
    # Prepare the OCR model
    BASE_MODEL_PATH = Path(".paddleocr/2.4/ocr")
    ocr = PaddleOCR(
        cls_model_dir=str(BASE_MODEL_PATH / "cls\\ch_ppocr_mobile_v2.0_cls_infer"),
        det_model_dir=str(BASE_MODEL_PATH / "det\\en\\en_ppocr_mobile_v2.0_det_infer"),
        rec_model_dir=str(BASE_MODEL_PATH / "rec\\en\\en_number_mobile_v2.0_rec_infer"),
        e2e_char_dict_path=str(Path("utils/ic15_dict.txt")),
        rec_char_dict_path=str(Path("utils/en_dict.txt")),
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
                init_tmp_dir()
                page_as_img, img_data, height, width = get_page_as_img(
                    pdf_files[current_doc]
                )
                vizWindow, graph = get_viz_window(height, width, img_data)

        if window == vizWindow:
            if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
                break

            if event == "-GRAPH-":  # if there's a "Graph" event, then it's a mouse
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
                info = window["info"]
                text = do_ocr(ocr, page_as_img, start_point, end_point)
                update_str = f"Page {current_doc * step + 1}/{len(pdf_files) * step} | "
                if text is not None:
                    update_str = update_str + f"Text: {text}"
                info.update(value=update_str)
                dragging = False
            elif event in (
                "OK",
                "e",
                "<Enter>",
            ):  # "e,<Enter>" key will behave like an "OK" event
                clean_tmp_dir(page_as_img)
                save_pdf(pdf_files[current_doc], destination_folder / f"{text}.pdf")
                if current_doc + 1 < len(pdf_files):
                    page_as_img, current_doc = viz_next_doc(
                        graph, pdf_files, current_doc
                    )
                    prior_rect = graph.draw_rectangle(
                        start_point, end_point, line_color="red"
                    )
                    text = do_ocr(ocr, page_as_img, start_point, end_point)
                    update_str = (
                        f"Page {current_doc * step + 1}/{len(pdf_files) * step} | "
                    )
                    if text is not None:
                        update_str = update_str + f"Text: {text}"
                    info.update(value=update_str)
                    start_point, end_point = None, None  # enable grabbing a new rect
                else:
                    sg.popup(
                        "All files have been processed! Exit now...", title="Notification",
                    )
                    break
            else:
                print("Unhandled event", event, values)
