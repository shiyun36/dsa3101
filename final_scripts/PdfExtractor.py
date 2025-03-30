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
    def __init__(self, insert_url, saved_url_file, country, industry):
        '''
        Input: saved_url_file, geographical region and instry 
        Intermediates: self.company_name, self.year and self.data (extracted esg text) are being generated. 
        Output: dataframe containing all the companies from one industry + region (eg. healthcare industry in SG) with the columns (esg_text, country, industry, company, year)
        Purpose: Extract company and year from pdf_url, and extract text from PDF using OCR scraper
        '''
        self.country = country
        self.industry = industry
        self.insert_url = insert_url
        self.saved_url_file = f"{os.path.splitext(saved_url_file)[0]}_{self.industry}_{self.geographical_region}.txt"
        # self.saved_url_file = saved_url_file ## Was using this as testing, once we have the url files with those changed names, shd run the above line instead of this. 
        self.company_name = None #Filled up with extract_company_and_year()
        self.year = None #Filled up with extract_company_and_year()

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
                if line and not line.startswith("#"):  
                    pdf_links.append(line)
        
        return pdf_links #[:1]

    
    def extract_company_and_year(self, pdf_url): 
        """
        Extracts company name and year from the PDF URL.
        Assumes company name is right after 'https://' and the year is just before '.pdf'.
        Note: Some companies may not follow this regex formatting, will need to build a more robust matching system, possible with a simple LLM. 
        """
        match = re.search(r'https://(?:www\.|.*?)?([a-zA-Z0-9-]+)\.com.*[_-]?(20\d{2}).*?\.pdf', pdf_url)
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
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

            response = requests.get(pdf_url, headers=headers)
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
        if self.insert_url == "":
            pdf_links = self.read_pdf_links()
        else:
            pdf_links = [self.insert_url]
        self.data = []  # Initialize an empty list to store all data

        for url in pdf_links: 
            try:
                # Extract company name and year from the URL
                self.extract_company_and_year(url)
        
                # Download and process the PDF
                ocr_pdf_data = self.download_pdf(url)
        
                # Extract text from the OCR'd PDF
                sentences = self.extract_text_from_pdf(ocr_pdf_data)
        
                # Prepare data for DataFrame
                for sentence in sentences:
                    self.data.append({
                        "company": self.company_name.upper(),
                        "year": self.year,
                        "country": self.country,   #I'm not sure if we want to save this as country or geographical region? I put geographical region because the initial pdf extractor step can look by countries, continents, or larger regions like APAC. SO I left it to be more general.  
                        "industry": self.industry,
                        "esg_text": sentence, 
                    })
            except requests.exceptions.HTTPError as http_err:
                            # Skip URLs that result in a 403 or any other HTTP error
                            logging.error(f"HTTP error occurred for {url}: {http_err}")
                            print(f"HTTP error occurred for {url}: {http_err}, skipping this link.")
        
            except requests.exceptions.RequestException as err:
                # Catch any other request errors
                logging.error(f"Error fetching {url}: {err}")
                print(f"Error fetching {url}: {err}, skipping this link.")

            except Exception as e:
                logging.error(f"Error processing PDF: {e}")
                continue
        
        # After processing all PDFs, return the DataFrame
        return pd.DataFrame(self.data)


# if __name__ == "__main__":
#     pdf_extractor = PDFExtractor(saved_url_file="../outputs/pdf_links.txt", 
#                            geographical_region='Singapore',
#                            industry='finance') 
#     df = pdf_extractor.process_pdf()
#     print(df.head(5))
    
