import re
import os
import json
import requests
import pandas as pd
from PyPDF2 import PdfReader
from io import BytesIO
import ocrmypdf


## This function takes in a pdf_url and outputs a dataframe with the columns (esg_text, country, industry, company, year)
def extract_text_company_year(pdf_url, country, industry):

    def extract_company_and_year(pdf_url):
        """
        Extracts company name and year from the PDF URL.
        Assumes company name is right after 'https://' and the year is just before '.pdf'.
        """
        match = re.search(r'https://(?:www\.)?([a-zA-Z0-9-]+).*?(\d{4}(?:-\d{4})?)\.pdf', pdf_url)
        if match:
            return match.group(1), match.group(2)
        else:
            print(f"Failed to extract company name and year from URL: {pdf_url}")
            return None, None

    def extract_text_from_pdf(pdf_bytes):
        """
        Extracts text from a PDF (after OCR is applied) and returns cleaned sentences.
        """
        def clean_page_text(text):
            """Removes headers, footers, and page numbers from extracted text."""
            lines = text.split("\n")
            if len(lines) > 2:
                lines = lines[2:]
            lines = [line for line in lines if not re.match(r'^(Page\s*\d+|\d+|P\.\s*\d+)$', line.strip(), re.IGNORECASE)]
            return "\n".join(lines)

        cleaned_text = ''
        pdfReader = PdfReader(pdf_bytes)
        
        for page in pdfReader.pages:
            raw_text = page.extract_text()
            if raw_text:
                cleaned_text += clean_page_text(raw_text) + ' '

        sentences = re.split(r'(?<=[.!?])\s+', cleaned_text.strip())
        final_sentences = [re.sub(r'\s+', ' ', sentence).strip() for sentence in sentences]
        
        return final_sentences
    
    data = []

    company_name, year = extract_company_and_year(pdf_url)

    if not company_name or not year:
        return pd.DataFrame(columns=["esg_text", "country", "industry", "company","year"])

    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        pdf_data = BytesIO(response.content)

        # Apply OCR
        ocr_pdf_data = BytesIO()
        ocrmypdf.ocr(pdf_data, ocr_pdf_data, force_ocr=True)
        ocr_pdf_data.seek(0)

        # Extract text from OCR'd PDF
        sentences = extract_text_from_pdf(ocr_pdf_data)

        for sentence in sentences:
            data.append({"esg_text": sentence, "country" : country, "industry": industry,
                         "company": company_name.upper(), "year": year})

        df = pd.DataFrame(data)
        return df
    
    except Exception as e:
        print(f"Error processing '{pdf_url}': {e}")
        return pd.DataFrame(columns=["esg_text", "country", "industry", "company", "year"])