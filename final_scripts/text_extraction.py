import pandas as pd
from PdfExtractor import PDFExtractor

def extract_esg_text(pdf_url, country, industry):
    pdf_extractor = PDFExtractor(pdf_url, country, industry)
    df = pdf_extractor.process_pdf()
    esg_text_df = df[["company", "year", "country", "industry", "esg_text"]]
    return esg_text_df
