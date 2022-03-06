import PySimpleGUI as sg
from borb.pdf.document.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF

############################### DEFINE FUNCTION #####################################


def splitPDF_1page(inputDir, outputDir):
    for file in inputDir.split(";"):
        with open(file, "rb") as current_pdf:
            input_pdf = PDF.loads(current_pdf)
        for i in range(0, int(input_pdf.get_document_info().get_number_of_pages())):
            output_pdf = Document()  # Create an empty document\
            # Adding pages to the empty document
            output_pdf.append_page(input_pdf.get_page(i))
            # Ouput name => this should be obtain from Hieu
            # This formula is temporary
            output_name = "output_" + str(i) + ".pdf"
            # Output directory
            output_full_path = outputDir + "\\" + output_name
            with open(output_full_path, "wb") as pdf_handled:
                PDF.dumps(pdf_handled, output_pdf)


def splitPDF_3pages(inputDir, outputDir):
    # Iterates through every single file in the selected files
    for file in inputDir.split(";"):
        with open(file, "rb") as current_pdf:
            input_pdf = PDF.loads(current_pdf)

        for i in range(0, int(input_pdf.get_document_info().get_number_of_pages()) - 2):
            if i % 3 == 0:
                output_pdf = Document()  # Create an empty document\
                # Adding pages to the empty document
                # if number_of_pages % 3 != 3: the remaining pages wont be published => need to fix this
                output_pdf.append_page(input_pdf.get_page(i))
                output_pdf.append_page(input_pdf.get_page(i + 1))
                output_pdf.append_page(input_pdf.get_page(i + 2))
                # Ouput name => this should be obtain from Hieu
                # This formula is temporary
                output_name = "output_" + str(i) + ".pdf"
                # Output directory
                output_full_path = outputDir + "\\" + output_name
                with open(output_full_path, "wb") as pdf_handled:
                    PDF.dumps(pdf_handled, output_pdf)


############################## CREATE UI ###########################################
sg.theme("LightGrey1")
layout = [[sg.Text(text="Choose destination folder: ",
                   justification="right",
                   size=(20, 1)),
           sg.Input(size=(50, 50),
                    pad=1, disabled=True),
           sg.FolderBrowse(key="-IN-",
                           size=(10, 1))],
          [sg.Text("Choose input PDF files: ",
                   justification="right",
                   size=(20, 1)),
              sg.Input(size=(50, 50),
                       pad=1, disabled=True),
              sg.FilesBrowse(key="-IN1-",
                             size=(10, 1))],
          [sg.Radio("Split 1 page per file", "RADIO1",
                    default=False,
                    key="-IN2-"),
           sg.Radio("Split 3 page per file", "RADIO1",
                    default=True,
                    key="-IN3-"),
           sg.Button("RUN",
                     size=(10, 1),
                     pad=((130, 10), (2, 2))),
           sg.Button("Cancel",
           size=(10, 1),
              pad=((10, 10), (2, 2)))]]

window = sg.Window("DOCUMENTS PROCESS AUTOMATION", layout, size=(650, 110))

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Cancel":
        break
    elif event == "RUN":
        # Errors handling
        # In case thang lon Dung khong select gi cả
        if values["-IN-"] == "":
            sg.popup("Please select the destination folder",
                     title="Notification")
            break
        if values["-IN1-"] == "":
            sg.popup("Please select the PDF files you need to split",
                     title="Notification",)
            break
        # store the link to destination folder
        destination_folder = values["-IN-"]
        PDF_files = values["-IN1-"]  # store the input PDF files
        if values["-IN3-"] == True:
            splitPDF_3pages(PDF_files, destination_folder)
        else:
            splitPDF_1page(PDF_files, destination_folder)
