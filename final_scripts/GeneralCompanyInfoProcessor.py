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
from RAGProcessor import retrieve_esg_text, get_reranked_docs
from db.scripts.db_general_company_info import insert_company_info

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
    def __init__(self, year, company, output_csv, saved_url_file):
        ''' 
        Inputs: 
        1. year: Extract general company information from this particular year
        2. company: Extract general company information from this particular company
        3. saved_url_file: esg reports url file path   
        '''
        self.year = year 
        self.company = company 
        self.output_csv = output_csv
        self.saved_url_file = saved_url_file
        self.query_template = (
            "Based on the web and your database, determine {metrics} of company {company} for its financial year of {year} from its sustainability reports. Provide a single, clear answer in the format: 'Final Answer: [value]' or an estimate if needed."
        )
        self.metrics = ['Name', 'Country', 'Continent', 'Industry', 'Year', 'GHG Scope 1 emission', 'GHG', 'Scope 2 emission', 'GHG Scope 3 emission', 'Water Consumption', 'Energy Consumption', 'Waste Generation', 'Total Employees', 'Total Female Employees', 'Employees under 30', 'Employees between 30-50', 'Employees above 50s', 'Fatalities', 'Injuries', 'Avg Training', 'Hours per employee' , 'Training Done, Independent Directors', 'Female Directors', 'Female Managers', 'Employees Trained', 'Certifications', 'Total Revenue', 'Total ESG Investment', 'Net Profit',' Debt-Equity Ratio', 'ROE', 'ROA']
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
        response = requests.get(endpoint, params=params)
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
        # Get web search context with truncated content.
        web_context = search_web(query, snippet_length=900)
    
        llm_openai = OpenAI(
            api_key=API_KEY,
            http_client=httpx.Client()
        )
    
        enhanced_prompt = (
            query +
            "\n\nWeb Search Results (most recent, truncated):\n" +
            web_context +
            "\n\nBased solely on the above search results, provide a single, clear answer in the format: 'Final Answer: [value]'."
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


    def extract_final_answer(text):
        """
        Extracts and returns the longest line starting with "Final Answer:".
        If no such line is found, returns the original text stripped.
        """
        answers = [line.strip() for line in text.splitlines() if line.strip().startswith("Final Answer:")]
        if not answers:
            return text.strip()
        return max(answers, key=len)

    def ask_openai_with_template(self):
        """
        Generates queries from a template using parameters, sends each query to OpenAI using only the internal database context,
        collects responses, and pivots the results so that the output CSV has one row per company/year.
        Each metric from the metrics file becomes a column header with its corresponding answer as the value.
        """
        company_tuple = (self.company, self.year)
        generic_query = f"{self.metrics}"
        year_str = str(self.year).strip()
        
        # Retrieve internal documents; if not found, the function will attempt to ingest PDFs online.
        internal_results = retrieve_esg_text(company_tuple, generic_query)
        reranked_docs = get_reranked_docs(generic_query, internal_results)
        # Format the query for this specific metric.
        query = self.query_template.format(company=self.company, year=year_str, Metric=self.metric)
        print(f"Querying OpenAI for: {query}")
        response_text = generate_openai_response(query, reranked_docs, company_tuple)["text"]
        response_text = extract_final_answer(response_text)
        if "Final Answer: NA" in response_text:
            fallback_query = (
                f"Based on web search, determine {self.metrics} of company {self.company} for its financial year of {year_str} "
                "from its sustainability reports. Provide a single, clear answer in the format: 'Final Answer: [value]'."
            )
            print(f"Internal answer was NA. Falling back to web search with query: {fallback_query}")
            fallback_response = query_openai_with_search(fallback_query)
            fallback_answer = fallback_response.get("text", "No answer generated")
            response_text = extract_final_answer(fallback_answer)
            key = (self.company, year_str)
        
        if key not in results:
            results[key] = {"company": self.company, "year": year_str}
        
        results[key][self.metrics] = response_text
        time.sleep(1)  # To avoid rapid-fire API calls
    
        rows = list(results.values())
        df = pd.DataFrame(rows)
        ## inserted db function here, pls check the headers of the df if it matches that if db_general_company_info script ##
        insert_company_info(df)
        ###
        df.to_csv(self.output_csv, index=False)
        print(f"Results saved to {self.output_csv}")
    
    
    def ask_openai_from_file(self):
        """
        Reads parameters from a CSV file, generates queries via a template,
        collects responses, and saves the responses to a CSV file where each metric is a separate column.
        """
        #self.parameters_list = self.final_df.to_dict('records')
        self.ask_openai_with_template()
    
   
if __name__ == "__main__":
    CompanyInfoProcessor = GeneralCompanyInfoProcessor(year = 2022,
                                                       company = 'pfizer', 
                                                       output_csv = "openai_responses.csv", 
                                                       saved_url_file = '/outputs') 
    CompanyInfoProcessor.testing()
    CompanyInfoProcessor.ask_openai_from_file()
