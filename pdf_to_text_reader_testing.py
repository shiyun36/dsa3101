from PyPDF2 import PdfReader
import re
import json


def convert_ocr_pdf_to_text(input_pdf_path, output_file):
    """
    Extract text from an OCR-based PDF, clean it, and save as a JSON list of sentences.
    """
    def clean_page_text(text):
        """
        Remove headers, footers, and page numbers from extracted text.
        """
        lines = text.split("\n")  # Split text into lines
        
        # Remove the first few lines (adjust as needed to remove the header)
        if len(lines) > 2:
            lines = lines[2:]

        # Remove page numbers using regex (common formats: "Page X", "X", "P. X")
        lines = [line for line in lines if not re.match(r'^(Page\s*\d+|\d+|P\.\s*\d+)$', line.strip(), re.IGNORECASE)]

        return "\n".join(lines)

    cleaned_text = ''
    pdfReader = PdfReader(input_pdf_path)

    for i in range(len(pdfReader.pages)):
        pageObj = pdfReader.pages[i]
        raw_text = pageObj.extract_text()
        
        if raw_text:
            processed_text = clean_page_text(raw_text)
            cleaned_text += processed_text + ' '  # separate pages with newlines
    
    sentences = re.split(r'(?<=[.!?])\s+', cleaned_text.strip())
    final_sentences = [re.sub(r'\n', ' ', sentence) for sentence in sentences] # places one sentence in a line
    final_sentences = [re.sub(r'\s+', ' ', sentence).strip() for sentence in sentences] # remove extra unnecessary white spaces

    # with open(output_file, "w", encoding = "utf-8") as f:
    #     json.dump(final_sentences, f, indent = 4, ensure_ascii = False)
    
    # print(f"Sentences saved to {output_file}")
    return final_sentences
    print('done')