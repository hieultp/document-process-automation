from pathlib import Path

import fitz


def split_pdf(inputDir, step=1):
    assert step >= 1, "step can only be positive number"
    results = []
    for file in map(Path, inputDir.split(";")):
        input_pdf: fitz.Document = fitz.Document(file)
        total_pages = input_pdf.page_count
        assert total_pages >= step
        for i in range(0, total_pages, step):
            doc = fitz.Document()
            doc.insert_pdf(input_pdf, from_page=i, to_page=i + step - 1)
            results.append(doc)

    return results
