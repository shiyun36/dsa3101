import pandas as pd
import time
import requests
import httpx
from bs4 import BeautifulSoup
from openai import OpenAI
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Disable tokenizers parallelism
import sys
import time
import re
import logging
logging.getLogger("ocrmypdf._metadata").setLevel(logging.ERROR)
logging.getLogger("ocrmypdf._exec.tesseract").setLevel(logging.ERROR)
import argparse
import pandas as pd
import torch
import torch.nn.functional as F
import httpx
from tqdm import tqdm
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from io import BytesIO
import ocrmypdf
import multiprocessing
from final_scripts.RAGProcessor import ESGAnalyzer

multiprocessing.set_start_method("spawn", force=True)

torch.set_default_device("cpu")
if torch.cuda.is_available():
    torch.set_default_device("cuda")
    print("Running on CUDA")

default_metrics_file = "./files/webscrape/metrics.csv"
API_KEY = os.getenv("API_KEY")  # OpenAI API Key
google_api_key = os.getenv("GOOGLE_API_KEY")  # Google API Key for Custom Search
cse_id = "40a230dc355fa46bf"  # Custom Search Engine ID


class GeneralCompanyInfoProcessor():
    def __init__(self, company, year, country,industry, output_csv, saved_url_file):
        ''' 
        Inputs: 
        1. year: Extract general company information from this particular year
        2. company: Extract general company information from this particular company
        3. saved_url_file: esg reports url file path   
        '''
        self.year = year 
        self.company = company 
        self.country = country 
        self.industry = industry 
        self.output_csv = output_csv
        self.saved_url_file = saved_url_file
        self.query_template = (
            "Based on context given, determine {metrics} of company {company} for its financial year of {year} from its sustainability reports. Provide a single, clear answer in the format: 'Final Answer: [Value]' or 'Final Answer: [Value per unit like mtc02e]'., If you cannot determine an answer reply with only 'Final Answer:NA'"
        )
        self.metrics = ['GHG Scope 1 emission', 'GHG Scope 2 emission', 'GHG Scope 3 emission', 'Water Consumption', 'Energy Consumption', 'Waste Generation', 'Total Employees', 'Total Female Employees', 'Employees under 30', 'Employees between 30-50', 'Employees above 50s', 'Fatalities', 'Injuries', 'Avg Training Hours per employee' , 'Training Done, Independent Directors', 'Female Directors', 'Female Managers', 'Employees Trained', 'Certifications', 'Total Revenue', 'Total ESG Investment', 'Net Profit',' Debt-Equity Ratio', 'ROE', 'ROA']
        df = pd.DataFrame({
    'Metric': self.metrics * len(self.company),
    'Year': self.year *  len(self.company) * len(self.metrics),
    'Company': self.company * len(self.metrics)
})
        df['Value'] = None
        self.final_df = df.pivot_table(index=['Company', 'Year'], columns='Metric', values='Value', aggfunc='first')

    # def extract_pdf_urls(self):
    #     all_links = []
    #     for filename in os.listdir(self.saved_url_file):
    #         if filename.endswith('.txt'):
    #             file_path = os.path.join(self.saved_url_file, filename)
                
    #             with open(file_path, 'r') as file:
    #                 content = file.read()
    #                 links = re.findall(r'https?://\S+', content)
    #                 all_links.extend(links)
    #         self.pdf_url = all_links
    #         return self.pdf_url


        # def company_year_exists(self.company, self.year):
    #     """
    #     Checks if documents for the given company and year already exist in ChromaDB.
    #     Returns True if documents exist, else False.
    #     """
    #     client = chromadb.PersistentClient(path="./chromadb_1003")
    #     collection = client.get_or_create_collection(name="dsa3101")
    #     # Normalize company name to uppercase for comparison.
    #     results = collection.query(
    #         query_texts=[""],
    #         n_results=1,
    #         where={"$and": [{"company": company.upper()}, {"year": int(year)}]}
    #     )
    #     if results.get("documents") and results["documents"][0]:
    #         return True
    #     return False
    
                    
    def testing(self):
        print(self.final_df.columns)
        print(self.final_df.head(5))

    
    def search_web(self, query, snippet_length=900):
        """
        Uses Google Custom Search API to retrieve content for the top results,
        but truncates each result to the first 'snippet_length' characters.
        """
        endpoint = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": google_api_key,
            "cx": cse_id,
            "q": query,
            "num": 5  # Retrieve top 5 results
        }
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        full_contents = []
    
        if "items" in data:
            for item in data["items"]:
                title = item.get("title", "")
                link = item.get("link", "")
                try:
                    page_response = requests.get(link, timeout=10)
                    page_response.raise_for_status()
                    soup = BeautifulSoup(page_response.content, "html.parser")
                    for s in soup(["script", "style"]):
                        s.decompose()
                    text = soup.get_text(separator=" ", strip=True)
                    # Truncate the text to reduce token count.
                    truncated_text = text[:snippet_length]
                except Exception as e:
                    truncated_text = f"Error fetching page: {e}"
                full_contents.append(f"{title} ({link}):\n{truncated_text}\n")
        return "\n".join(full_contents)


    def query_openai_with_search(self, query):
        """
        Incorporates web search results (with truncated content) into the prompt and sends it to OpenAI.
        """
    
        llm_openai = OpenAI(
            api_key=API_KEY,
            http_client=httpx.Client()
        )
    
        enhanced_prompt = (
            query +
            "\n\nBased on the above metric, provide a single, clear answer in the format: Final Answer: '[Value]' or Final Answer: '[Value per unit like mtc02e]'."
        )
    
        retries = 3
        while retries > 0:
            try:
                response = llm_openai.chat.completions.create(
                    model="gpt-4o-mini-search-preview",
                    messages=[
                        {
                            "role": "assistant",
                            "content": "You are an expert in ESG analysis. Rely only on the provided, up-to-date web search results to answer the query."
                        },
                        {"role": "user", "content": enhanced_prompt},
                    ]
                )
                return {"text": response.choices[0].message.content.strip()}
            except Exception as e:
                print(f"API Error encountered: {e}. Retrying after delay...")
                retries -= 1
                time.sleep(5)
        return {"text": "API Error: Unable to generate response after retries."}


    def extract_final_answer(self, text):
        """
        Extracts and returns the substring after the last occurrence of "Final Answer:".
         the result spans multiple lines, only the first line is returned.
        If no such substring is found, returns the original text stripped.
        """
        prefix = "Final Answer:"
        if prefix in text:
            # Use rpartition to split on the last occurrence.
            answer = text.rpartition(prefix)[2].strip()
            # If the answer contains multiple lines, take only the first line.
            answer = answer.splitlines()[0].strip()
            return answer
        return text.strip()


    def ask_openai_with_template(self):
        """ writes the results to a CSV file.
        """
        company_tuple = (self.company, self.year)
        year_str = str(self.year).strip()
        results = {}  # To store responses for each metric
    
        # Instantiate the ESGAnalyzer with the appropriate ESG text DataFrame.
        # (Here we assume an empty dictionary is acceptable for esg_text_df.)
        esg_analyzer = ESGAnalyzer(esg_text_df={})
    
        for metric in self.metrics:
            # Format the query for the current metric.
            query = self.query_template.format(company=self.company, year=year_str, metrics=metric)
            print(f"Querying OpenAI for metric '{metric}': {query}")

            # Retrieve internal documents for the metric.
            internal_results = esg_analyzer.retrieve_esg_text(company_tuple=company_tuple, query=query)
            reranked_docs = esg_analyzer.get_reranked_docs(query=query, results=internal_results)

            # Generate a response using the internal documents.
            response = esg_analyzer.generate_openai_response(query=query, reranked_docs=reranked_docs, company_tuple=company_tuple)
            response_text = response.get("text", "").strip()
            response_text = self.extract_final_answer(response_text)
        
            # Check if the response is "NA" and, if so, fall back to a web search query.
            if "Final Answer: NA" or "Final Answer:NA"  in response_text:
                print("NA found!")
                fallback_query = (
                    f"Search the web and help me determine the {metric} of company {self.company} for its financial year of {year_str}. Provide a single, numeric value as an answer in the format: Final Answer: '[Value]' or Final Answer: '[Value per unit like mtc02e]'. If you cannot determine an answer reply with only 'Final Answer:NA'"
                )
                print(f"Internal answer for metric '{metric}' was NA.")
                fallback_response = self.query_openai_with_search(fallback_query)
                fallback_answer = fallback_response.get("text", "No answer generated")
                print(f"Fallback answer for metric '{metric}': {fallback_answer}")
                response_text = self.extract_final_answer(fallback_answer)
        
            # Store the final answer for this metric.
            results[metric] = response_text
        
            time.sleep(1)  # To avoid rapid-fire API calls
        print(self.country,self.industry)
    # Build a single-row dictionary for this company/year.
        base_info = {"Company": self.company, "Year": year_str, "Country": self.country, "Industry": self.industry}
        output_row = base_info.copy()
        output_row.update(results)
        print("Output row:", output_row)
        df = pd.DataFrame([output_row])
        if os.path.exists(self.output_csv):
            df.to_csv(self.output_csv, mode='a', header=False, index=False)
        else:
            df.to_csv(self.output_csv, index=False)
    
    
    def ask_openai_from_file(self):
        """"
        collects responses, and saves the responses to a CSV file
        """
        #self.parameters_list = self.final_df.to_dict('records')
        self.ask_openai_with_template()
    
   
if __name__ == "__main__":
    CompanyInfoProcessor = GeneralCompanyInfoProcessor(year = 2024,
                                                       company = 'PUMAENERGY',
                                                       country = 'USA',  # Replace with the appropriate country
                                                       industry = 'Energy',  # Replace with the appropriate industry
                                                       output_csv = "openai_responses.csv",
                                                       saved_url_file = '/outputs')
    CompanyInfoProcessor.testing()
    CompanyInfoProcessor.ask_openai_from_file()
