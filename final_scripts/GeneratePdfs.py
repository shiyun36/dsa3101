import os
import datetime
import logging
import re
from googlesearch import search  # Ensure you have installed 'google-search-results'
from openai import OpenAI  # For Gemini API
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Setup logging
log_file = "pdf_scraper.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class GeneratePdfs:
    def __init__(self, output_file="pdf_links.txt", years=None):
        """
        Initializes the scraper with an output file and years to scrape reports for.
        :param output_file: The file where PDF links will be stored.
        :param years: A list of years to fetch ESG reports for.
        """
        self.output_file = output_file
        self.years = years if years else [2024, 2023, 2022, 2021]
        self.company_list = self.generate_company_names()
    
    def generate_company_names(self):
        """
        Uses Gemini API to generate random company names from different industries and countries.
        :return: A list of company names.
        """
        client = OpenAI(api_key=GOOGLE_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Generate a diverse list of companies from different industries and countries."},
                {"role": "user", "content": "Can you randomly generate a list of company names from different sizes, industries, and countries? Examples include Pfizer, Apple, Uber, and LVMH."}
            ]
        )

        if response.choices:
            generated_text = response.choices[0].message.content
            company_names = [name for name in re.findall(r"\*\*(.+?)\:\*\*", generated_text) if "Disclaimer" not in name]
            return company_names
        
        logging.error("Failed to generate company names.")
        return []

    def fetch_pdf_links(self):
        """
        Searches Google for ESG report PDFs based on company names and years.
        :return: A list of PDF links.
        """
        pdf_links = []

        for company in self.company_list:
            for year in self.years:
                query = f"{company} {year} ESG report filetype:pdf"
                try:
                    for url in search(query, num_results=1):
                        if url.endswith(".pdf"):
                            pdf_links.append(url)
                            logging.info(f"Found PDF: {url}")
                except Exception as e:
                    logging.error(f"Error fetching {query}: {e}")
        
        return pdf_links

    def save_links(self, pdf_links):
        """
        Saves the fetched PDF links to the specified output file.
        :param pdf_links: List of ESG report links.
        """
        if pdf_links:
            with open(self.output_file, "a") as f:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n# Links fetched on {timestamp}\n")
                f.writelines(f"{link}\n" for link in pdf_links)
            logging.info(f"Saved {len(pdf_links)} PDF links to {self.output_file}")
        else:
            logging.warning("No PDF links found.")

    def run(self):
        """
        Runs the full scraping process.
        """
        pdf_links = self.fetch_pdf_links()
        self.save_links(pdf_links)

if __name__ == "__main__":
    scraper = ESGReportScraper(output_file="esg_pdf_links.txt", years=[2024, 2023, 2022])
    scraper.run()
