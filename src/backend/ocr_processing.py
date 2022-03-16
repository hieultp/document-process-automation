from pathlib import Path
from typing import List, Tuple

import numpy as np
from fitz import Document, Matrix, Pixmap
from paddleocr import PaddleOCR
from PIL import Image

from .pdf_processing import save_pdf, split_pdf


class Processor(PaddleOCR):
    def __init__(self, doc2img_scale: float = 1.25, **kwargs):
        super().__init__(**kwargs)

        self.doc2img_scale = doc2img_scale
        self.dst_folder: Path = None
        self.pdf_files: List[Document] = []
        self.total_docs = 0
        self.current_doc = -1
        self.img = None  # Hold current image corresponding to current_doc

    def add_documents(self, pdf_filepaths, step: int = 1):
        self.pdf_files += split_pdf(pdf_filepaths, step=step)
        self.total_docs += len(self.pdf_files)

    def save_document(self, fname: str):
        save_pdf(self.pdf_files[self.current_doc], self.dst_folder / f"{fname}.pdf")

    def get_doc_as_img(self, doc_idx: int, page: int = 0, scale: float = None):
        if scale is None:
            scale = self.doc2img_scale

        pix: Pixmap = (
            self.pdf_files[doc_idx]
            .load_page(page_id=page)
            .get_pixmap(matrix=Matrix(scale, scale))
        )
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        return img, pix.tobytes("ppm")

    def __next__(self):
        if self.current_doc + 1 < self.total_docs:
            self.current_doc += 1
            self.img, img_data = self.get_doc_as_img(self.current_doc)
            return img_data
        else:
            raise StopIteration

    def ocr(
        self,
        start_point: Tuple[int, int],
        end_point: Tuple[int, int],
    ) -> str:
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

        crop = self.img.crop((x1, y1, x2, y2))
        text = super().ocr(np.asarray(crop), det=False)
        return text[0][0] if text else ""