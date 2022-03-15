from pathlib import Path

import PySimpleGUI as sg

from src.backend import Processor
from src.frontend.ui import get_main_window, get_viz_window

sg.theme("LightGrey1")
sg.set_options(dpi_awareness=True)


def viz_next_doc(graph: sg.Graph, img_data, img_id: int):
    graph.delete_figure(img_id)
    img_id = graph.draw_image(data=img_data, location=(0, 0))
    graph.send_figure_to_back(img_id)
    return img_id


def do_info_update(window, current_doc, total_files, step=1, ocr_text=None):
    window["-INFO-"].update(value=f"Page {current_doc * step + 1}/{total_files * step}")
    window["-OCR-STR-"].update(value=ocr_text if ocr_text is not None else "")


if __name__ == "__main__":
    # Prepare the OCR model
    BASE_MODEL_PATH = Path(".paddleocr/2.4/ocr")
    BASE_PPOCR_UTILS_PATH = Path(".paddleocr/ppocr/utils")
    processor = Processor(
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

    img_data = None
    img_id = None
    step = None

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
                processor.dst_folder = Path(values["-OUT-DIR-"])
                step = 1 if values["-ONE-PAGE-"] else 3
                processor.add_documents(values["-IN-PDFS-"], step)

                mainWindow.hide()

                # Init visualization window
                img_data = next(processor)
                vizWindow, graph, img_id = get_viz_window(
                    processor.img.height, processor.img.width, img_data
                )
                vizWindow["-OCR-STR-"].block_focus(block=True)
                do_info_update(
                    vizWindow, processor.current_doc, processor.total_docs, step
                )

        if window == vizWindow:
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

                text = processor.ocr(start_point, end_point)
                do_info_update(
                    window,
                    processor.current_doc,
                    processor.total_docs,
                    step,
                    ocr_text=text,
                )

                dragging = False
                start_point = end_point = None  # enable grabbing a new rect
            elif event in ("OK", "e"):  # "e,<Enter>" key will behave like an "OK" event
                if (
                    event == "e"
                    and window.FindElementWithFocus() == window["-OCR-STR-"]
                ):  # Handle case where event "e" is in the input box
                    continue

                processor.save_document(values["-OCR-STR-"])

                try:
                    img_data = next(processor)
                    img_id = viz_next_doc(graph, img_data, img_id)
                    text = processor.ocr(*graph.get_bounding_box(prior_rect))
                    do_info_update(
                        window,
                        processor.current_doc,
                        processor.total_docs,
                        step,
                        ocr_text=text,
                    )
                except StopIteration:
                    sg.popup(
                        "All files have been processed! Exit now...",
                        title="Notification",
                    )
                    vizWindow.close()
                    vizWindow = None
                    mainWindow.un_hide()
