from dotenv import load_dotenv
import os
import re
import chromadb  # Vector Database
from tqdm import tqdm
import json
import time 
import torch.nn.functional as F
import pandas as pd
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from tqdm import tqdm  
from sklearn.metrics.pairwise import cosine_similarity
import sys
import httpx
import logging
from openai import OpenAI

API_KEY = os.getenv('API_KEY')
print(API_KEY)

class RAGProcessor:
    def __init__(self, db_path="./chromadb_1003", api_key=API_KEY, client=None, file_path):
        '''
        Given a json file containing a (a) value query and (b) score query per metric, 
        The output dataframe will containt the (a) extracted values and (b) score of each metric. 
        
        '''
        self.db_path = db_path
        self.api_key = api_key
        self.client = client if client else httpx.Client()
        self.llm_openai = OpenAI(api_key=self.api_key, http_client=self.client)
        self.file_path = file_path

        # Set device to CUDA if available
        if torch.cuda.is_available():
            torch.set_default_device("cuda")
            print("Running on CUDA")
        else:
            torch.set_default_device("cpu")

        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_or_create_collection(name="dsa3101")

    def company_year_exists(self, company, year):
        """Check if a company-year pair already exists in the database"""
        results = self.collection.query(
            query_texts=[""],  # Empty query as we filter solely by metadata
            n_results=1,
            where={
                "$and": [
                    {"company": company},
                    {"year": int(year)}
                ]
            }
        )
        return bool(results.get("documents") and results["documents"][0])

    def add_documents_from_df(self):
        """Add documents from a DataFrame to ChromaDB"""
         try:
            df = pd.read_csv(self.file_path)
        except pd.errors.ParserError as e:
            logging.error(f"Parser error while loading {self.file_path}: {e}")
            return
        except Exception as e:
            logging.error(f"Failed to load {self.file_path}: {e}")
            return
    
        # Capture the starting document count to keep doc_ids consistent
        groups = df.groupby(["company", "year"])

        for (company, year), group_df in tqdm(groups, total=len(groups), desc="Processing groups", unit="group", ncols=100):
            if self.company_year_exists(company, int(year)):
                print(f"Group for {company} ({year}) already exists. Skipping.")
                continue
            starting_count = self.collection.count()
            
            # Use tqdm to show progress in adding documents
             for i, (_, row) in enumerate(group_df.iterrows()):
                 doc_text = row["esg_text"]
                 doc_company = row["company"]
                 doc_year = int(row["year"])
                 doc_industry = row["industry"]
                 doc_country = row["country"]
                
                 doc_id = f"doc_{starting_count + i}"
                 print(f"Adding document {doc_id} for {doc_company} ({doc_year})")
                 self.collection.add(
                     ids=[doc_id],
                     documents=[doc_text],
                     metadatas=[{
                         "company": doc_company, 
                         "year": doc_year, 
                         "industry": doc_industry,
                          "country": doc_country
                         }]
                     )

    def generate_openai_response(self, query, reranked_docs, company_tuple):
        """Generate response from OpenAI based on reranked documents"""
        context = "\n\n".join(reranked_docs)
        prompt = f"""You are an expert in ESG analysis. Please reason through step by step and then provide the final answer to the query. 
        Please verify your answer against the context provided, and rewrite the answer if inconsistent. Below is a question and relevant retrieved documents.
        
        Question: {query}
        Context: {context + "End of Context"}
        """

        retries = 3
        while retries > 0:
            try:
                response = self.llm_openai.chat.completions.create(
                    model="gpt-3.5-turbo",  # or your preferred model
                    messages=[
                        {"role": "assistant", "content": "You are an expert in ESG analysis looking through several documents"},
                        {"role": "user", "content": prompt},
                    ]
                )
                if response and response.choices:
                    return {"text": response.choices[0].message.content.strip()}
                retries -= 1
                time.sleep(2)
            except Exception as e:
                retries -= 1
                time.sleep(5)
        return "API Error: Unable to generate response after retries."

    def rerank_documents(self, query, retrieved_docs):
        """Rerank retrieved documents based on their relevance to the query"""
        reranker_model_name = "BAAI/bge-reranker-base"
        reranker_tokenizer = AutoTokenizer.from_pretrained(reranker_model_name)
        reranker_model = AutoModelForSequenceClassification.from_pretrained(reranker_model_name)

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

    def retrieve_company_metadata(self, company_tuple):
        """Retrieve metadata for a specific company from ChromaDB"""
        results = self.collection.query(
            query_texts=[""],
            n_results=1,
            where={"$and": [{"company": company_tuple[0]}, {"year": int(company_tuple[1])}]}
        )
        if not results.get("documents") or not results["documents"][0]:
            print(f"Company '{company_tuple[0]}' for year '{company_tuple[1]}' is not in the database. Exiting.")
            sys.exit(1)

        metadata = results["metadatas"][0][0]
        return metadata

    def retrieve_esg_text(self, company_tuple, query):
        """Retrieve ESG text from ChromaDB"""
        results = self.collection.query(
            query_texts=[query],
            n_results=15,
            where={"$and": [{"company": company_tuple[0]}, {"year": int(company_tuple[1])}]}
        )
        if not results.get("documents") or not results["documents"][0]:
            print(f"Company '{company_tuple[0]}' for year '{company_tuple[1]}' is not in the database. Exiting.")
            sys.exit(1)
        return results

    def compute_linear_score(self, extracted_values, scoring_query, company_tuple):
        """Compute linear score from the extracted values"""
        final_answer_generator = 'Return your answer as: "Final Answer: X" (where X is a numeric or clearly defined answer)'
        score = self.generate_openai_response(scoring_query + final_answer_generator, str(extracted_values), company_tuple)
        return score

    def extract_absolute_score(self, score):
        """Extract the numerical score from the generated response"""
        matches = re.findall(r"(?:Final\s*Answer|Answer).*?([-+]?\d*\.?\d+)(?:\s*\%\.)?", str(score), re.DOTALL)
        return float(matches[-1]) if matches else "N/A"

    def process_company(self, company_tuple):
        """Process a specific company's ESG data"""
        metadata = self.retrieve_company_metadata(company_tuple)
        country = metadata.get("country", "").strip().lower()
        industry = metadata.get("industry", "").strip().lower()

        # Load query and scoring files based on country and industry
        query_file, csv_file = self.select_files_based_on_metadata(country, industry)

        try:
            with open(query_file, "r") as file:
                esg_metrics = json.load(file)
        except Exception as e:
            print(f"Error loading JSON file '{query_file}': {e}")
            sys.exit(1)

        headers = self.prepare_headers(esg_metrics)
        df_columns = ["Company", "Year", "Industry", "Country"] + headers
        df_existing, existing_companies = self.load_existing_data(csv_file, df_columns)

        if tuple(company_tuple) + (industry, country) in existing_companies:
            print(f"Company '{company_tuple[0]}' for year '{company_tuple[1]}' already processed.")
            return None, csv_file, df_columns

        row_data = self.extract_esg_data(company_tuple, esg_metrics)

        return row_data, csv_file, df_columns

    def select_files_based_on_metadata(self, country, industry):
        """Select query and CSV files based on country and industry"""
        if country == "singapore":
            if industry == "finance":
                return "../files/scoring_queries/sg_bank_query.json", "../notebooks/extractValues/sg_finance_score.csv"
            elif industry == "health":
                return "../files/scoring_queries/sg_healthcare_query.json", "../notesbooks/extractValues/sg_healthcare_score.csv"
        print(f"Unsupported country '{country}' or industry '{industry}'. Exiting.")
        sys.exit(1)

    def prepare_headers(self, esg_metrics):
        """Prepare DataFrame headers based on ESG metrics"""
        headers = []
        for item in esg_metrics:
            metric_name = list(item.keys())[0]
            headers.append(metric_name)
            headers.append(f"{metric_name}_numScore")
        return headers

    def load_existing_data(self, csv_file, df_columns):
        """Load existing CSV data if available"""
        if os.path.exists(csv_file):
            df_existing = pd.read_csv(csv_file)
            existing_companies = set(map(tuple, df_existing[['Company', 'Year', "Industry", "Country"]].values.tolist()))
        else:
            print("Creating new CSV file.")
            df_existing = pd.DataFrame(columns=df_columns)
            existing_companies = set()
        return df_existing, existing_companies

    def extract_esg_data(self, company_tuple, esg_metrics):
        """Extract ESG data for a given company"""
        row_data = {"Company": company_tuple[0], "Year": company_tuple[1], "Industry": esg_metrics["industry"], "Country": esg_metrics["country"]}
        for metric_item in tqdm(esg_metrics, desc="Extracting ESG Metrics"):
            for metric, details in metric_item.items():
                query = details["value_query"]
                scoring_thresholds = details["scoring_query"]
                retrieved_text = self.retrieve_esg_text(company_tuple, query)
                extracted_values = self.extract_values(query, retrieved_text, company_tuple)
                score = self.compute_linear_score(extracted_values, scoring_thresholds, company_tuple)
                row_data[metric] = extracted_values
                row_data[f"{metric}_numScore"] = self.extract_absolute_score(score)
        return row_data
