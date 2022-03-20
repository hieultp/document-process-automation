from pathlib import Path

from fitz import Document


def split_pdf(inputDir: str, pages_per_doc: int = 1):
    assert pages_per_doc >= 1, "pages_per_doc can only be positive number"
    results = []
    for file in map(Path, inputDir.split(";")):
        input_pdf: Document = Document(file)
        total_pages = input_pdf.page_count
        assert total_pages >= pages_per_doc
        for i in range(0, total_pages, pages_per_doc):
            doc = Document()
            doc.insert_pdf(input_pdf, from_page=i, to_page=i + pages_per_doc - 1)
            results.append(doc)

    return results


def save_pdf(input_pdf: Document, filename: Path):
    total_pages = input_pdf.page_count
    if total_pages == 1:
        input_pdf.save(filename)
    elif total_pages == 3:
        for page in range(total_pages):
            doc = Document()
            doc.insert_pdf(input_pdf, from_page=page, to_page=page)
            if page == 0:
                current_name = filename.name
            elif page == 1:
                current_name = f"{filename.stem}co.pdf"
            elif page == 2:
                current_name = f"{filename.stem}bl.pdf"
            doc.save(filename.with_name(current_name))
    else:
        raise ValueError(f"Total pages {total_pages} has not been implemented")
