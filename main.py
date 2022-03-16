from pathlib import Path

import PySimpleGUI as sg

from src.backend import Processor
from src.frontend import GUI

sg.theme("LightGrey1")
sg.set_options(dpi_awareness=True)


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

    gui = GUI(processor)
    gui.show()
