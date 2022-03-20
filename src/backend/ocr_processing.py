from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
from fitz import Document, Matrix, Pixmap
from paddleocr import PaddleOCR
from PIL import Image

from .pdf_processing import delete_pdf, save_pdf, split_pdf


class Processor(PaddleOCR):
    def __init__(self, doc2img_scale: float = 1.25, **kwargs):
        super().__init__(**kwargs)

        self.doc2img_scale = doc2img_scale
        self.dst_folder: Path = None
        self.pdf_files: List[Document] = []
        self.total_docs = 0
        self.current_doc = -1
        self.pages_per_doc = 0
        self.current_page = 1  # Current page in the original pdf
        self.img = None  # Hold current image corresponding to current_doc
        self.processed_filenames: List[Path] = []

    def add_documents(self, pdf_filepaths, pages_per_doc: int = 1):
        self.pages_per_doc = pages_per_doc
        self.current_page -= pages_per_doc
        self.pdf_files += split_pdf(pdf_filepaths, pages_per_doc)
        self.total_docs += len(self.pdf_files)

    def get_total_pages(self, doc_idx=-1):
        total_pages = 0
        if doc_idx == -1:
            for pdf_file in self.pdf_files:
                total_pages += pdf_file.page_count
        elif doc_idx < -1:
            raise ValueError("Argument doc_idx should not be less than -1")
        else:
            total_pages = self.pdf_files[doc_idx].page_count
        return total_pages

    def save_document(self, fname: str):
        processed_filename = self.dst_folder / f"{fname}.pdf"
        self.processed_filenames.append(processed_filename)
        save_pdf(self.pdf_files[self.current_doc], processed_filename)

    def delete_prev_saved_doc(self):
        fname = self.processed_filenames.pop()
        delete_pdf(fname, self.pages_per_doc)
        return fname.stem  # Return only the name of the file (without extension)

    def get_doc_as_img(self, doc_idx: int, page: int = 0):
        pix: Pixmap = (
            self.pdf_files[doc_idx]
            .load_page(page_id=page)
            .get_pixmap(matrix=Matrix(self.doc2img_scale, self.doc2img_scale))
        )
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        img_data = pix.tobytes("ppm")
        return img, img_data

    def next_doc(self):
        if self.current_doc + 1 < self.total_docs:
            self.current_doc += 1
            self.current_page += self.pages_per_doc
            self.img, img_data = self.get_doc_as_img(self.current_doc)
            return self.img, img_data
        else:
            return None

    def previous_doc(self):
        if self.current_doc - 1 < self.total_docs:
            self.current_doc -= 1
            self.current_page -= self.pages_per_doc
            self.img, img_data = self.get_doc_as_img(self.current_doc)
            return img_data
        else:
            return None

    def ocr(self, start_point: Tuple[int, int], end_point: Tuple[int, int],) -> str:
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
        try:
            # FIXME:
            # This is know to have cv2 error due to numerical error in cv2.
            # The only thing we could do now is to ignore this exception.
            text = super().ocr(np.asarray(crop), det=False)
        except cv2.error as error:
            print(error)
            return ""
        else:
            return text[0][0] if text else ""

    def reset(self):
        self.dst_folder: Path = None
        self.pdf_files: List[Document] = []
        self.total_docs = 0
        self.current_doc = -1
        self.pages_per_doc = 0
        self.current_page = 1
        self.img = None
