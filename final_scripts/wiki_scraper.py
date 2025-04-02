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
import chromadb
from tqdm import tqdm
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from io import BytesIO
import ocrmypdf
import multiprocessing
import scraper2

# Force multiprocessing to use spawn (instead of fork)
if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)

# Set device (defaults to CPU, but will switch to CUDA if available)
torch.set_default_device("cpu")
if torch.cuda.is_available():
    torch.set_default_device("cuda")
    print("Running on CUDA")

# Global variable: default path to the metrics CSV file
default_metrics_file = "./files/webscrape/metrics.csv"
GPT_API_KEY = os.getenv("GPT_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set your OpenAI API key here

def store_esg_report_in_chromadb(company, year, industry, country, esg_text):
    client = chromadb.PersistentClient(path="./chromadb_1003")
    collection = client.get_or_create_collection(name="dsa3101")
    doc_id = f"doc_{company}_{year}_{int(time.time())}"
    collection.add(
        ids=[doc_id],
        documents=[esg_text],
        metadatas=[{"company": company, "year": int(year), "industry": industry, "country": country}]
    )
    logging.info(f"Stored ESG report for {company} ({year}) as {doc_id}")

#############################################
# PDF Extraction via PDFExtractor Class
#############################################

class PDFExtractor:
    def __init__(self, saved_url_file=None, country="unknown", industry="unknown", company_name=None, year=None):
        """
        Initialize the extractor.
        Either provide a saved_url_file containing PDF URLs (one per line)
        OR provide company_name and year to search for PDFs online.
        The resulting DataFrame will have columns: esg_text, country, industry, company, year.
        """
        self.saved_url_file = saved_url_file
        self.country = country
        self.industry = industry
        self.company_name = company_name
        self.year = year
        self.data = []

    def read_pdf_links(self):
        if not self.saved_url_file or not os.path.exists(self.saved_url_file):
            logging.warning("Saved URL file not provided or not found.")
            return []
        pdf_links = []
        with open(self.saved_url_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    pdf_links.append(line)
        return pdf_links

    def search_pdf_links(self, company, year, num_results=2):
        query = f"{company} {year} ESG report filetype:pdf"
        google_api_key = GOOGLE_API_KEY
        cse_id = "40a230dc355fa46bf"
        endpoint = "https://www.googleapis.com/customsearch/v1"
        params = {"key": google_api_key, "cx": cse_id, "q": query, "num": num_results}
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        pdf_links = []
        if "items" in data:
            for item in data["items"]:
                link = item.get("link", "")
                if link.lower().endswith(".pdf"):
                    pdf_links.append(link)
        return pdf_links

    def extract_company_and_year(self, pdf_url):
        match = re.search(r'https://(?:www\.)?([a-zA-Z0-9-]+).*?(\d{4}(?:-\d{4})?)\.pdf', pdf_url)
        if match:
            self.company_name = match.group(1)
            self.year = match.group(2)
        else:
            logging.error(f"Failed to extract company name and year from URL: {pdf_url}")
            raise ValueError("Company name and year could not be extracted from the URL.")

    def download_pdf(self, pdf_url):
        try:
            response = requests.get(pdf_url)
            response.raise_for_status()
            pdf_data = BytesIO(response.content)
            ocr_pdf_data = BytesIO()
            try:
                ocrmypdf.ocr(pdf_data, ocr_pdf_data, force_ocr=True)
                ocr_pdf_data.seek(0)
                return ocr_pdf_data
            except Exception as e:
                logging.error(f"Error during OCR for PDF URL '{pdf_url}': {e}")
                # Ignore OCR errors and return None so that this PDF is skipped.
                return None
        except Exception as e:
            logging.error(f"Error downloading or processing PDF from '{pdf_url}': {e}")
            # Ignore download errors and return None so that this PDF is skipped.
            return None



    def extract_text_from_pdf(self, pdf_bytes):
        def clean_page_text(text):
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

    def process_pdf(self):
        if self.saved_url_file and os.path.exists(self.saved_url_file):
            pdf_links = self.read_pdf_links()
        else:
            if not self.company_name or not self.year:
                raise ValueError("Either a saved_url_file must be provided or company_name and year must be set for online search.")
            pdf_links = self.search_pdf_links(self.company_name, self.year)
    
        for url in pdf_links:
            # Output the link to the PDF that was pulled from online.
            print(f"Pulled PDF URL: {url}")
            if self.saved_url_file:
                self.extract_company_and_year(url)
            ocr_pdf_data = self.download_pdf(url)
            # If download_pdf returns None due to any error, skip to the next link.
            if ocr_pdf_data is None:
                continue
            sentences = self.extract_text_from_pdf(ocr_pdf_data)
            for sentence in sentences:
                self.data.append({
                    "esg_text": sentence,
                    "country": self.country,
                    "industry": self.industry,
                    "company": self.company_name.upper() if self.company_name else "UNKNOWN",
                    "year": self.year if self.year else "0"
                })
        return pd.DataFrame(self.data)


#############################################
# Ingestion Function: Add Documents from DataFrame
#############################################

def add_documents_from_df(df):
    """
    Add df that has 'esg_text', 'company', 'year', 'industry', 'country'.
    Each row is added as a separate document into ChromaDB.
    """
    client = chromadb.PersistentClient(path="./chromadb_1003")
    collection = client.get_or_create_collection(name="dsa3101")

    # Group by (company, year)
    groups = df.groupby(["company", "year"])
    for (company, year), group_df in tqdm(groups, total=len(groups), desc="Processing groups", unit="group", ncols=100):
        if company_year_exists(company, year):
            print(f"Group for {company} ({year}) already exists. Skipping all documents for this group.")
            continue
        starting_count = collection.count()
        for i, (_, row) in enumerate(group_df.iterrows()):
            doc_text = row["esg_text"]
            doc_company = row["company"]
            doc_year = int(row["year"])
            doc_industry = row["industry"]
            doc_country = row["country"]
            doc_id = f"doc_{starting_count + i}"
            print(f"Adding document {doc_id} for {doc_company} ({doc_year})")
            collection.add(
                ids=[doc_id],
                documents=[doc_text],
                metadatas=[{
                    "company": doc_company,
                    "year": doc_year,
                    "industry": doc_industry,
                    "country": doc_country
                }]
            )

def company_year_exists(company, year):
    """
    Checks if documents for the given company and year already exist in ChromaDB.
    Returns True if documents exist, else False.
    """
    client = chromadb.PersistentClient(path="./chromadb_1003")
    collection = client.get_or_create_collection(name="dsa3101")
    # Normalize company name to uppercase for comparison.
    results = collection.query(
        query_texts=[""],
        n_results=1,
        where={"$and": [{"company": company.upper()}, {"year": int(year)}]}
    )
    if results.get("documents") and results["documents"][0]:
        return True
    return False

#############################################
# Query and ESG Metrics Functions (Internal DB Only)
#############################################

def generate_openai_response(query, reranked_docs, company_tuple):
    llm_openai = OpenAI(api_key=API_KEY, http_client=httpx.Client())
    print(f"Extracting ESG context for Company: {company_tuple[0]}, Year: {company_tuple[1]}")
    context = "\n\n".join(reranked_docs)
    prompt = f"""You are an expert in ESG analysis. Please reason through step by step and then provide the final answer.
Verify your answer against the context provided.
Below is a question and the relevant ESG report context.

Question: "{query}"

Context:
{context}
End of Context
"""
    retries = 3
    while retries > 0:
        try:
            response = llm_openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "assistant", "content": "You are an expert in ESG analysis reviewing a report."},
                    {"role": "user", "content": prompt},
                ],
            )
            if response and response.choices:
                print(prompt)
                return {"text": response.choices[0].message.content.strip()}
            else:
                print("Empty completion received. Retrying...")
                retries -= 1
                time.sleep(2)
        except Exception as e:
            print(f"API Error: {e}. Retrying after delay...")
            retries -= 1
            time.sleep(5)
    return {"text": "API Error: Unable to generate response after retries."}

def rerank_documents(query, retrieved_docs):
    reranker_model_name = "BAAI/bge-reranker-base"
    reranker_tokenizer = AutoTokenizer.from_pretrained(reranker_model_name)
    reranker_model = AutoModelForSequenceClassification.from_pretrained(reranker_model_name)
    if not retrieved_docs:
        return []
    query_inputs = reranker_tokenizer(query, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        query_outputs = reranker_model(**query_inputs, output_hidden_states=True)
    query_embedding = query_outputs.hidden_states[-1][:, 0]
    doc_inputs = reranker_tokenizer(retrieved_docs, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        doc_outputs = reranker_model(**doc_inputs, output_hidden_states=True)
    doc_embeddings = doc_outputs.hidden_states[-1][:, 0]
    similarities = F.cosine_similarity(query_embedding, doc_embeddings, dim=-1)
    sorted_indices = similarities.argsort(descending=True)
    reranked_docs = [retrieved_docs[i] for i in sorted_indices.tolist()]
    return reranked_docs

def get_reranked_docs(query, results):
    # Handle case when results is None
    if results is None or "documents" not in results or not results["documents"][0]:
        print("No documents found for reranking.")
        return []
    
    combined_text = " ".join(results["documents"][0])
    sentences = re.split(r'(?<=[.!?])\s+', combined_text)
    sentences = [s for s in sentences if s.strip()]
    reranked_sentences = rerank_documents(query, sentences)
    return reranked_sentences

def retrieve_esg_text(company_tuple, query):
    chroma_client = chromadb.PersistentClient(path="./chromadb_1003")
    collection = chroma_client.get_or_create_collection(name="dsa3101")
    # Normalize company name to uppercase in the query and retrieve 15 results.
    results = collection.query(
        query_texts=[query],
        n_results=15,
        where={"$and": [{"company": company_tuple[0].upper()}, {"year": int(company_tuple[1])}]}
    )
    
    if not results.get("documents") or not results["documents"][0]:
        print(f"Company '{company_tuple[0]}' for year '{int(company_tuple[1])}' is not in the database. Proceeding to search online.")
        
        # Use PDFExtractor to search for and process the PDFs
        extractor = PDFExtractor(company_name=company_tuple[0], year=company_tuple[1])
        df_pdf = extractor.process_pdf()  # Process the PDFs and add text to the dataframe
        
        # Add documents to ChromaDB if the DataFrame is not empty
        if not df_pdf.empty:
            print("Ingesting extracted PDF sentences into ChromaDB...")
            add_documents_from_df(df_pdf)
            # Optional: Wait a short while for ingestion to complete
            time.sleep(2)
            # Re-query the collection after ingestion
            results = collection.query(
                query_texts=[query],
                n_results=15,
                where={"$and": [{"company": company_tuple[0].upper()}, {"year": int(company_tuple[1])}]}
            )
            if not results.get("documents") or not results["documents"][0]:
                print("No documents found even after ingestion.")
                return None
        else:
            print("No PDFs found during online search.")
            return None

    # Print the top 15 documents before reranking.
    original_docs = results["documents"][0]
    print("Top 15 documents from retrieval:")
    for i, doc in enumerate(original_docs[:15]):
        print(f"Doc {i+1}: {doc}\n")
    
    # Combine the list of document strings into one single string
    combined_text = " ".join(original_docs)
    results["documents"][0] = [combined_text]
    return results



def answer_metrics_for_company(company, year, metrics_file, output_csv="esg_answers.csv"):
    # Normalize company name to uppercase here.
    company_tuple = (company.upper(), float(year))
    df_metrics = pd.read_csv(metrics_file)
    if "Metric" in df_metrics.columns:
        metrics_list = df_metrics["Metric"].tolist()
    else:
        metrics_list = df_metrics.iloc[:, 0].tolist()
    generic_query = "ESG sustainability report"
    results = retrieve_esg_text(company_tuple, generic_query)
    reranked_docs = get_reranked_docs(generic_query, results)
    answers_dict = {"Company": company, "Year": year}
    for metric in metrics_list:
        metric_query = (
            f"Based on the internal database, determine {metric} of company {company} "
            f"for its financial year of {year} from its sustainability reports. "
            "Provide a single, clear answer in the format: 'Final Answer: [value]'. Return 'NA' if there is no answer"
        )
        answer_response = generate_openai_response(metric_query, reranked_docs, company_tuple)
        answer_text = answer_response.get("text", "No answer generated")
        answers_dict[metric] = answer_text
        print(f"Answer for {metric}: {answer_text}")
    if os.path.exists(output_csv):
        df = pd.read_csv(output_csv)
        df = df.append(answers_dict, ignore_index=True)
    else:
        df = pd.DataFrame([answers_dict])
    df.to_csv(output_csv, index=False)
    print(f"Answers saved to {output_csv}")

#############################################
# CSV Merging and Query Template Functions
#############################################

def merge_parameters_csv(metrics_file, company_file, year_file, output_file="parameters.csv"):
    try:
        df_metrics = pd.read_csv(metrics_file)
        df_company = pd.read_csv(company_file)
        df_year = pd.read_csv(year_file)
    except Exception as e:
        print(f"Error reading one of the CSV files: {e}")
        raise
    df_metrics.columns = df_metrics.columns.str.lower()
    df_company.columns = df_company.columns.str.lower()
    df_year.columns = df_year.columns.str.lower()
    print("Metrics columns:", df_metrics.columns.tolist())
    print("Company columns:", df_company.columns.tolist())
    print("Year columns:", df_year.columns.tolist())
    if len(df_metrics) == len(df_company) == len(df_year):
        combined_df = pd.concat([df_metrics, df_company, df_year], axis=1)
    else:
        df_metrics['key'] = 1
        df_company['key'] = 1
        df_year['key'] = 1
        combined_df = df_metrics.merge(df_company, on='key').merge(df_year, on='key').drop('key', axis=1)
    combined_df.to_csv(output_file, index=False)
    print(f"Combined parameters CSV created at '{output_file}'.")
    return output_file

def extract_final_answer(text):
    """
    Extracts and returns the longest line starting with "Final Answer:".
    If no such line is found, returns the original text stripped.
    """
    answers = [line.strip() for line in text.splitlines() if line.strip().startswith("Final Answer:")]
    if not answers:
        return text.strip()
    return max(answers, key=len)


def ask_openai_with_template(query_template, parameters_list, output_csv):
    results = {}
    for params in parameters_list:
        # Convert values to strings and strip whitespace; provide defaults if missing.
        company = str(params.get("company", "unknown")).strip()
        year_str = str(params.get("year", "0")).strip()
        metric = str(params.get("metric") or params.get("Metric") or params.get("metrics") or "unknown metric").strip()

        # Debug: print the row being processed.
        print("Processing row:", params)
        
        # Attempt to convert year to float; if fails, use 0.
        try:
            year_float = float(year_str)
        except ValueError:
            year_float = 0
        
        # Skip row if missing or default values.
        if company.lower() == "unknown" or year_float == 0 or metric.lower() == "unknown metric":
            print("Skipping row due to missing or default values:", params)
            continue

        # Normalize company name to uppercase for the tuple.
        company_tuple = (company.upper(), year_float)
        # Use a generic query for internal retrieval.
        generic_query = f"{metric}"
        
        # Retrieve internal documents; if not found, the function will attempt PDF ingestion.
        internal_results = retrieve_esg_text(company_tuple, generic_query)
        reranked_docs = get_reranked_docs(generic_query, internal_results)
        # Format the query using the CSV metric value.
        query = query_template.format(company=company, year=year_str, Metric=metric)
        print(f"Querying OpenAI for: {query}")
        response_text = generate_openai_response(query, reranked_docs, company_tuple)["text"]
        # Extract only the "Final Answer:" portion.
        response_text = extract_final_answer(response_text)

        # Check if the internal answer is "Final Answer: NA"
        if "Final Answer: NA" in response_text:
            fallback_query = (
                f"Based on web search, determine {metric} of company {company} for its financial year of {year_str} "
                "from its sustainability reports. Provide a single, clear answer in the format: 'Final Answer: [value]'."
            )
            print(f"Internal answer was NA. Falling back to web search with query: {fallback_query}")
            fallback_response = scraper2.query_openai_with_search(fallback_query)
            fallback_answer = fallback_response.get("text", "No answer generated")
            fallback_answer = extract_final_answer(fallback_answer)
            print(f"Fallback answer for {metric}: {fallback_answer}")
            response_text = fallback_answer

        key = (company, year_str)
        if key not in results:
            results[key] = {"company": company, "year": year_str}
        results[key][metric] = response_text
        time.sleep(1)  # To avoid rapid-fire API calls
        
    rows = list(results.values())
    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")

def ask_openai_from_file(query_template, parameters_file, output_csv):
    try:
        df_params = pd.read_csv(parameters_file)
    except Exception as e:
        print(f"Error reading parameters file: {e}")
        raise
    parameters_list = df_params.to_dict('records')
    ask_openai_with_template(query_template, parameters_list, output_csv)

#############################################
# Main: Ingestion and Query Workflow
#############################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ESG Ingestion and Query Script with CSV inputs for company and year.")
    parser.add_argument("--ingest_csv", type=str, help="Path to the ESG documents CSV file (with pre-extracted text) to ingest")
    parser.add_argument("--pdf_csv", type=str, help="Path to the CSV file containing PDF URLs for ESG reports")
    parser.add_argument("--company_csv", type=str, required=True, help="Path to the company CSV file")
    parser.add_argument("--year_csv", type=str, required=True, help="Path to the year CSV file")
    parser.add_argument("--metrics_csv", type=str, default=default_metrics_file, help="Path to the metrics CSV file")
    parser.add_argument("--output_csv", type=str, default="openai_responses.csv", help="Output CSV for ESG metric answers")
    parser.add_argument("--pdf_extractor", type=str, help="Path to a file containing PDF URLs for extraction via PDFExtractor")
    parser.add_argument("--country", type=str, help="Country for PDF extraction (if using PDFExtractor)", default="unknown")
    parser.add_argument("--industry", type=str, help="Industry for PDF extraction (if using PDFExtractor)", default="unknown")
    args = parser.parse_args()

    # Step 1: Ingest documents from a text CSV if provided.
    if args.ingest_csv:
        print("Starting text document ingestion...")
        # Pre-extracted text ingestion code (if needed) goes here.
        print("Text document ingestion complete.")

    # Step 2: Ingest PDF-based ESG reports by searching for PDF links using company and year.
    if args.pdf_csv:
        print("Starting PDF document ingestion by search...")
        df_company = pd.read_csv(args.company_csv)
        df_year = pd.read_csv(args.year_csv)
        for i in range(len(df_company)):
            company = df_company.iloc[i]["company"]
            year = df_year.iloc[i]["year"]
            print(f"Processing company: {company}, year: {year}")
            extractor = PDFExtractor(company_name=company, year=year, country="unknown", industry="unknown")
            df_pdf = extractor.process_pdf()  # Process the PDFs and get the DataFrame
            if not df_pdf.empty:
                print(f"Adding documents from {company} ({year}) to ChromaDB...")
                add_documents_from_df(df_pdf)  # Add extracted documents to ChromaDB
            else:
                print(f"No PDFs found for {company} ({year}).")
        print("PDF document ingestion complete.")

    # Step 3: Ingest PDFs using the PDFExtractor if a pdf_extractor file is provided.
    if args.pdf_extractor:
        print("Starting PDF ingestion via PDFExtractor...")
        try:
            df_extracted = pd.read_csv(args.pdf_extractor, header=None, names=["pdf_url"])
        except Exception as e:
            logging.error(f"Error reading PDF extractor file: {e}")
            df_extracted = pd.DataFrame(columns=["pdf_url"])
        
        from PdfExtractor import PDFExtractor  # Ensure PdfExtractor.py is accessible.
        extractor = PDFExtractor(args.pdf_extractor, args.country, args.industry)
        df_pdf = extractor.process_pdf()
        
        if not df_pdf.empty:
            print("Ingesting extracted PDF sentences into ChromaDB...")
            add_documents_from_df(df_pdf)
        else:
            print("No data extracted from PDF. Skipping ingestion.")
        print("PDF extraction ingestion complete.")

    # Step 4: Merge parameters from metrics, company, and year CSV files.
    print("Merging parameters CSV...")
    parameters_file = merge_parameters_csv(args.metrics_csv, args.company_csv, args.year_csv)
    print(f"Parameters CSV merged and saved as '{parameters_file}'.")

    # Step 5: Define query template and generate queries using only internal database context.
    print("Starting ESG metric queries...")
    query_template = (
        "Based on the internal database, determine {Metric} of company {company} for its financial year of {year} from its sustainability reports. "
        "Provide a single, clear answer in the format: 'Final Answer: [value]'. Return 'NA' if there is no answer. Leave the steps to obtain the value out of the answer"
    )
    ask_openai_from_file(query_template, parameters_file, args.output_csv)
    print(f"ESG metric answers saved to '{args.output_csv}'.")