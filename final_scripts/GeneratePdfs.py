import os
import datetime
import logging
import re
from googlesearch import search  
from google import genai
from dotenv import load_dotenv
load_dotenv()


# Setup logging


class GeneratePdfs:
    def __init__(self, output_file, log_file, years, industry, country, GOOGLE_API_KEY):
        """
        Initializes the scraper with an output file and years to scrape reports for.
        :param output_file: The file where PDF links will be stored.
        :param years: A list of years to fetch ESG reports for.
        """
        self.years = years 
        self.industry = industry
        self.country = country
        self.output_file = f"{os.path.splitext(output_file)[0]}_{self.industry}_{self.country}.txt"
        self.log_file = f"{os.path.splitext(log_file)[0]}_{self.industry}_{self.country}.log"
        logging.basicConfig(filename=self.log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.GOOGLE_API_KEY = GOOGLE_API_KEY
        self.company_list = self.generate_company_names()
        
    def generate_company_names(self):
        """
        Uses Gemini API to generate random company names from different industries and countries.
        :return: A list of company names.
        """
        client = genai.Client(api_key=self.GOOGLE_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash", #deepseek/deepseek-r1-zero:free
            contents=f"Can you randomly generate 3 comapnies in the {self.industry} in {self.country}, that are most likely to have ESG reports publicly available. Please only output the names of the companies"
        )
        print(response.text)
        if response and hasattr(response, 'text') and response.text:
            company_names = [name for name in re.findall(r"\*\*(.+?)\:\*\*", response.text) if "Disclaimer" not in name]
            return company_names
        
        logging.error("Failed to generate company names.")
        return []

    def fetch_pdf_links_from_web(self):
        """
        Searches Google for ESG report PDFs based on company names and years.
        :return: A log file with the PDF links that can be found from the web.
        """
        pdf_links = set()  
        for company in self.company_list:
            for year in self.years:
                query = f"{company} {year} ESG report filetype:pdf"
                try:
                    for url in search(query, num_results=1):
                        if url.endswith(".pdf"):
                            pdf_links.add(url)
                            logging.info(f"Found PDF: {url}")
                            print(f"Found PDF: {url}")
                except Exception as e:
                    logging.error(f"Error fetching {query}: {e}")
        return list(pdf_links)
        

    def save_links(self, pdf_links):
        """
        Saves the fetched PDF links to the specified log file.
        :param pdf_links: List of ESG report links.
        """        
        pdf_links = list(set(pdf_links)) 
        print('pdf_links are', pdf_links)
        print(self.output_file, self.log_file)
        
        if pdf_links:
            with open(self.output_file, "a") as f:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n# Links fetched on {timestamp}\n")
                f.writelines(f"{link}\n" for link in pdf_links)
            print(f"Saved {len(pdf_links)} PDF links to {self.output_file}")
        else:
            print("No PDF links found.")

    
    def run(self):
        """
        Runs the full scraping process.
        """
        pdf_links = self.fetch_pdf_links_from_web() #fetch_pdf_links_from_logs
        self.save_links(pdf_links)
        

if __name__ == "__main__":
    pdf_links_generator = GeneratePdfs(output_file="../outputs/pdf_links.txt", 
                           log_file = "../loggings/pdf_scraper.log",
                           years=[2024, 2023, 2022, 2021],
                           industry='energy', 
                           country='singapore',
                           GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")) 
    pdf_links_generator.run()
