import re
import os
import json
import requests
import pandas as pd
from PyPDF2 import PdfReader
from io import BytesIO
import ocrmypdf
import logging

class PDFExtractor:
    def __init__(self, saved_url_file, country, industry):
        '''
        Input: pdf_url 
        Output: dataframe with the columns (esg_text, country, industry, company, year)
        Purpose: Extract company and year from pdf_url, and extract text from PDF using OCR scraper
        '''
        self.saved_url_file = saved_url_file
        ohh#self.pdf_url = pdf_url
        self.country = country
        self.industry = industry
        self.company_name = None
        self.year = None
        self.data = []

    def read_pdf_links(self):
        """
        Reads the stored PDF links from the output file.
        :return: A list of PDF links.
        """
        if not os.path.exists(self.saved_url_file):
            logging.error(f"Output file {self.saved_url_file} not found!")
            return []
        
        pdf_links = []
        with open(self.saved_url_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):  # Ignore timestamp lines
                    pdf_links.append(line)
        
        return pdf_links

    
    def extract_company_and_year(self, pdf_url):
        """
        Extracts company name and year from the PDF URL.
        Assumes company name is right after 'https://' and the year is just before '.pdf'.
        """
        match = re.search(r'https://(?:www\.)?([a-zA-Z0-9-]+).*?(\d{4}(?:-\d{4})?)\.pdf', pdf_url)
        if match:
            self.company_name = match.group(1)
            self.year = match.group(2)
        else:
            logging.error(f"Failed to extract company name and year from URL: {pdf_url}")
            raise ValueError("Company name and year could not be extracted from the URL.")
    
    def extract_text_from_pdf(self, pdf_bytes):
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
    
    def download_pdf(self, pdf_url):
        """
        Downloads the PDF from the provided URL and applies OCR to extract the text.
        """
        try:
            response = requests.get(pdf_url)
            response.raise_for_status()
            pdf_data = BytesIO(response.content)

            # Apply OCR
            ocr_pdf_data = BytesIO()
            ocrmypdf.ocr(pdf_data, ocr_pdf_data, force_ocr=True)
            ocr_pdf_data.seek(0)

            return ocr_pdf_data
        except Exception as e:
            logging.error(f"Error downloading or processing PDF from '{pdf_url}': {e}")
            raise Exception(f"Error downloading or processing PDF from '{pdf_url}'.")

    def process_pdf(self):
        """
        Main method to extract information from the PDF and return the result as a DataFrame.
        """
        try:
            # Extract company name and year from the URL
            for url in pdf_links: 
                pdf_url = url 
                self.extract_company_and_year(url)
    
                # Download and process the PDF
                ocr_pdf_data = self.download_pdf(url)
    
                # Extract text from the OCR'd PDF
                sentences = self.extract_text_from_pdf(ocr_pdf_data)
    
                # Prepare data for DataFrame
                for sentence in sentences:
                    self.data.append({
                        "esg_text": sentence,
                        "country": self.country,
                        "industry": self.industry,
                        "company": self.company_name.upper(),
                        "year": self.year
                    })
    
                # Return the results as a DataFrame
                return pd.DataFrame(self.data)
        
        except Exception as e:
            logging.error(f"Error processing PDF: {e}")
            return pd.DataFrame(columns=["company", "year""country", "industry", "esg_text"])

# Example usage:
# def main(saved_url_file, country, industry):
#     pdf_extractor = PDFExtractor(pdf_url, country, industry)
#     result_df = pdf_extractor.process_pdf()
#     return result_df

# To call the function:
# pdf_url = "http://example.com/path/to/pdf.pdf"
# country = "Singapore"
# industry = "Finance"
# df = main(pdf_url, country, industry)
# print(df)
