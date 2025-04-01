import os
import datetime
import logging
import re
from googlesearch import search  
from dotenv import load_dotenv
import google.generativeai as genai
load_dotenv()


# Setup logging
def remove_first_dot(path):
    # Remove only the first dot at the start of the string.
    return re.sub(r'^\.', '', path, count=1)

class GeneratePdfs:
    def __init__(self, output_file, log_file, years, industry, geographical_region, GOOGLE_API_KEY):
        """
         the scraper with an output file and years to scrape reports for.
        :param output_file: The file where PDF links will be stored.
        :param years: A list of years to fetch ESG reports for.

        
        """

        self.years = years 
        self.industry = industry
        self.geographical_region = geographical_region
        # Create dynamic filenames based on the industry and geographical_region
        self.output_file = remove_first_dot(f"{os.path.splitext(output_file)[0]}_{self.industry}_{self.geographical_region}.txt")
        self.log_file = f"{os.path.splitext(log_file)[0]}_{self.industry}_{self.geographical_region}.log"

        output_dir = os.path.dirname(self.output_file)
        log_dir = os.path.dirname(self.log_file)
        
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging. The log file will be created automatically if it doesn't exist.
        logging.basicConfig(filename=self.log_file, level=logging.INFO, 
                        format="%(asctime)s - %(levelname)s - %(message)s")
    
        self.GOOGLE_API_KEY = GOOGLE_API_KEY
        self.company_list = self.generate_company_names()
        
    def generate_company_names(self):
        """
        Uses Gemini API to generate random company names from different industries and countries.
        :return: A list of company names.
        """
        genai.configure(api_key=self.GOOGLE_API_KEY)
        llm_genai = genai.GenerativeModel('gemini-2.0-flash')
        response = llm_genai.generate_content(
            contents=f"Can you randomly generate 3 comapnies in the {self.industry} in {self.geographical_region}, that are most likely to have ESG reports publicly available. Please only output the names of the companies"
        )
        if response and response.text:
            company_names = company_names = re.findall(r'^\d+\.\s*(.*)$', response.text, re.MULTILINE)

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
    pdf_links_generator = GeneratePdfs(output_file="./outputs/pdf_links.txt", 
                           log_file = "./loggings/pdf_scraper.log",
                           years=[2024, 2023, 2022, 2021],
                           industry='energy', 
                           geographical_region='Singapore',
                           GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")) 
    print("generating pdf links...")
    pdf_links_generator.run()
