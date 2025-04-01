import os
import re
import json
import time
import sys
import logging
import pandas as pd
from tqdm import tqdm

import torch
import torch.nn.functional as F
from transformers import AutoModelForSequenceClassification, AutoTokenizer

import chromadb  # Vector Database
import httpx
from dotenv import load_dotenv

# Load environment variables and set torch device
load_dotenv()
torch.set_default_device("cpu")
if torch.cuda.is_available():
    torch.set_default_device("cuda")
    print("running on cuda")

from openai import OpenAI

class ESGAnalyzer:
    def __init__(self,esg_text_df, chroma_db_path="./chromadb_1003", collection_name="dsa3101", openai_api_key=None):
        print("Initializing ESGAnalyzer...")
        # Initialize API key from environment or passed value.
        self.openai_api_key = openai_api_key or os.getenv("API_KEY")
        self.esg_text_df = esg_text_df
        # Set up ChromaDB client and collection.
        self.client = chromadb.PersistentClient(path=chroma_db_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        # Initialize OpenAI client.
        self.llm_openai = OpenAI(api_key=self.openai_api_key, http_client=httpx.Client())
        # Load the re-ranker model and tokenizer.
        self.reranker_model_name = "BAAI/bge-reranker-base"
        self.reranker_tokenizer = AutoTokenizer.from_pretrained(self.reranker_model_name)
        self.reranker_model = AutoModelForSequenceClassification.from_pretrained(self.reranker_model_name)

    def company_year_exists(self, company, year):
        results = self.collection.query(
            query_texts=[""],
            n_results=1,
            where={"$and": [{"company": company}, {"year": int(year)}]}
        )
        if results.get("documents") and results["documents"][0]:
            return True
        return False

    def add_documents_from_csv(self, file_path):
        """Add documents from CSV to ChromaDB."""
        try:
            df = pd.read_csv(file_path)
        except pd.errors.ParserError as e:
            logging.error(f"Parser error while loading {file_path}: {e}")
            return
        except Exception as e:
            logging.error(f"Failed to load {file_path}: {e}")
            return

        groups = df.groupby(["company", "year"])
        for (company, year), group_df in tqdm(groups, total=len(groups), desc="Processing groups", unit="group", ncols=100):
            if self.company_year_exists(company, int(year)):
                print(f"Group for {company} ({year}) already exists. Skipping all documents for this group.")
                continue
            starting_count = self.collection.count()
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

    def add_documents_from_df(self, df):
        """
        Add documents from a DataFrame that has 'esg_text', 'company', 'year', 'industry', and 'country' columns.
        """
        groups = df.groupby(["company", "year"])
        for (company, year), group_df in tqdm(groups, total=len(groups), desc="Processing groups", unit="group", ncols=100):
            if self.company_year_exists(company, year):
                print(f"Group for {company} ({year}) already exists. Skipping all documents for this group.")
                continue
            starting_count = self.collection.count()
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
        """Retrieve context from ChromaDB and generate an answer using OpenAI."""
        print(f"Extracting, Company: {company_tuple[0]}, Year: {company_tuple[1]}")
        context = "\n\n".join(reranked_docs)
        prompt = f"""You are an expert in ESG analysis. Please reason through step by step and then provide the final answer to the query. 
Please verify your answer against the context provided, and rewrite the answer if inconsistent. Below is a question and relevant retrieved documents.

Question: {query}

Context:
{context + "End of Context"}

"""
        retries = 3
        while retries > 0:
            try:
                response = self.llm_openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "assistant", "content": "You are an expert in ESG analysis looking through several documents"},
                        {"role": "user", "content": prompt},
                    ],
                )
                if response and response.choices:
                    return {"text": response.choices[0].message.content.strip()}
                else:
                    print("Empty completion received. Retrying...")
                    retries -= 1
                    time.sleep(2)
            except Exception as e:
                print(f"API Error encountered: {e}. Retrying after delay...")
                retries -= 1
                time.sleep(5)
        return "API Error: Unable to generate response after retries."

    def rerank_documents(self, query, retrieved_docs):
        """Re-rank documents using cosine similarity over re-ranker embeddings."""
        if not retrieved_docs:
            return []
        query_inputs = self.reranker_tokenizer(query, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            query_outputs = self.reranker_model(**query_inputs, output_hidden_states=True)
        query_embedding = query_outputs.hidden_states[-1][:, 0]
        doc_inputs = self.reranker_tokenizer(retrieved_docs, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            doc_outputs = self.reranker_model(**doc_inputs, output_hidden_states=True)
        doc_embeddings = doc_outputs.hidden_states[-1][:, 0]
        similarities = F.cosine_similarity(query_embedding, doc_embeddings, dim=-1)
        sorted_indices = similarities.argsort(descending=True)
        reranked_docs = [retrieved_docs[i] for i in sorted_indices.tolist()]
        return reranked_docs

    def retrieve_company_metadata(self, company_tuple):
        """
        Query the collection to retrieve metadata for a given company.
        Expects company_tuple to be (company_name, year).
        """
        results = self.collection.query(
            query_texts=[""],
            n_results=1,
            where={"$and": [{"company": company_tuple[0]}, {"year": int(company_tuple[1])}]}
        )
        if not results.get("documents") or not results["documents"][0]:
            print(f"Company '{company_tuple[0]}' for year '{company_tuple[1]}' is not in the database. Exiting.")
            sys.exit(1)
        metadata = results["metadatas"][0][0]
        if "country" not in metadata or "industry" not in metadata:
            print(f"Metadata for {company_tuple[0]} is missing 'country' or 'industry' fields. Exiting.")
            sys.exit(1)
        return metadata

    def retrieve_esg_text(self, company_tuple, query):
        """Retrieve ESG text from ChromaDB for a company given a specific query."""
        results = self.collection.query(
            query_texts=[query],
            n_results=15,
            where={"$and": [{"company": company_tuple[0]}, {"year": int(company_tuple[1])}]}
        )
        if not results.get("documents") or not results["documents"][0]:
            print(f"Company '{company_tuple[0]}' for year '{int(company_tuple[1])}' is not in the database. Exiting.")
            sys.exit(1)
        return results

    def get_reranked_docs(self, query, results):
        retrieved_docs = [doc for doc in results["documents"][0]]
        reranked_docs = self.rerank_documents(query, retrieved_docs)
        return reranked_docs

    def extract_values(self, query, results, company_tuple):
        reranked_docs = self.get_reranked_docs(query, results)
        response = self.generate_openai_response(query, reranked_docs, company_tuple)
        return response

    def compute_linear_score(self, extracted_values, scoring_query, company_tuple):
        final_answer_generator = 'Return your answer as: "Final Answer: X" (where X is a numeric or clearly defined answer)'
        score = self.generate_openai_response(scoring_query + final_answer_generator, str(extracted_values), company_tuple)
        return score

    def extract_absolute_score(self, score):
        matches = re.findall(r"(?:Final\s*Answer|Answer).*?([-+]?\d*\.?\d+)(?:\s*\%\.)?", str(score), re.DOTALL)
        return float(matches[-1]) if matches else "N/A"

    def process_company(self, company_tuple):
        metadata = self.retrieve_company_metadata(company_tuple)
        country = metadata.get("country", "").strip().lower()
        industry = metadata.get("industry", "").strip().lower()
        
        # Choose JSON query file and CSV file based on country and industry.
        if country == "singapore":
            if industry == "finance":
                query_file = "./files/scoring_queries/sg_bank_query.json"
                csv_file = "./files/rag_output/sg_finance_score.csv"
            elif industry == "health":
                query_file = "./files/scoring_queries/sg_healthcare_query.json"
                csv_file = "./files/rag_output/sg_healthcare_score.csv"
            elif industry == "energy":
                query_file = "./files/scoring_queries/sg_energy_query.json"
                csv_file = "./files/rag_output/sg_energy_score.csv"
            elif industry == "e-commerce":
                query_file = "./files/scoring_queries/sg_tech_query.json"
                csv_file = "./files/rag_output/sg_tech_score.csv"
            else:
                query_file = "./files/scoring_queries/generalMetrics.json"
                csv_file = "./files/rag_output/unsupported_company_scores.csv"
                print(f"Unsupported industry '{industry}' for country '{country}'. Using General Metrics.")
        else:
            query_file = "./files/scoring_queries/generalMetrics_query.json"
            csv_file = "./files/rag_output/unsupported_company_scores.csv"
            print(f"Unsupported country '{country}'. Using General Metrics.")

        # Load the ESG metrics from the JSON file.
        try:
            with open(query_file, "r") as file:
                esg_metrics = json.load(file)
        except Exception as e:
            print(f"Error loading JSON file '{query_file}': {e}")
            sys.exit(1)
        
        headers = []
        for item in esg_metrics:
            metric_name = list(item.keys())[0]
            headers.append(metric_name)
            headers.append(f"{metric_name}_numScore")
        df_columns = ["Company", "Year", "Industry", "Country"] + headers

        if os.path.exists(csv_file):
            df_existing = pd.read_csv(csv_file)
            existing_companies = set(map(tuple, df_existing[['Company', 'Year', "Industry", "Country"]].values.tolist()))
        else:
            print("Path to CSV file does not exist. Creating a new one.")
            df_existing = pd.DataFrame(columns=df_columns)
            existing_companies = set()

        if tuple(company_tuple) + (industry, country) in existing_companies:
            print(f"Company '{company_tuple[0]}' for year '{company_tuple[1]}' already processed; skipping.")
            return None, csv_file, df_columns

        row_data = {"Company": company_tuple[0], "Year": company_tuple[1], "Industry": industry, "Country": country}

        for metric_item in esg_metrics:
            for metric, details in metric_item.items():
                metric_name = metric
                query_value = details["value_query"]
                scoring_thresholds = details["scoring_query"]

                retrieved_text = self.retrieve_esg_text(company_tuple, query_value)
                extracted_values = self.extract_values(query_value, retrieved_text, company_tuple)
                score = self.compute_linear_score(extracted_values, scoring_thresholds, company_tuple)
                
                row_data[metric_name] = {"extracted_values": extracted_values, "score": score}
                row_data[metric_name + '_numScore'] = self.extract_absolute_score(score)

        return row_data, csv_file, df_columns

    def extract_esgreports(self,companies):
    
        final_dataframes = {}
        new_rows = {}
        len_new_rows = 0
        for company_tuple in companies:
            row_data, csv_file, df_columns = self.process_company(company_tuple)

            # If no row_data, skip
            if row_data is None:
                print("No new data to add.")
                continue

        # If this CSV hasn't been seen yet, initialize a new entry
            if csv_file not in new_rows:
                new_rows[csv_file] = {"rows": [], "columns": df_columns}

        # Add the row data to our in-memory collection
            new_rows[csv_file]["rows"].append(row_data)

        if((new_rows[csv_file]) == "None"):
            print("No new Data to add")


    # Once all rows are collected, write or append them to their respective CSVs
        for csv_file, data in new_rows.items():

            df_new = pd.DataFrame(data["rows"], columns=data["columns"])
            final_df = pd.DataFrame(data["rows"], columns=data["columns"])

            if os.path.exists(csv_file):
                df_existing = pd.read_csv(csv_file)
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            else:
                df_combined = df_new

            df_combined.to_csv(csv_file, index=False)

            final_dataframes[csv_file] = df_combined
            len_new_rows = len(data['rows'])
            print(f"Added {len(data['rows'])} new companies to {csv_file}.")



        return csv_file , len_new_rows


    def rag_main(self):
        print("Starting RAG process...")

        new_companies_df = self.esg_text_df
        if not isinstance(new_companies_df, pd.DataFrame):
            raise TypeError(f"Input must be a pandas DataFrame, got {type(new_companies_df)} instead.")
        # First, add documents to the ChromaDB from the dataframe.
        print("Adding documents to ChromaDB...")
        self.add_documents_from_df(new_companies_df)
        
        # Extract the unique company-year pairs.
        subset = new_companies_df[['company', 'year']]
        unique_pairs = subset.drop_duplicates()
        unique_pairs['year'] = unique_pairs['year'].astype(int)
        company_year_tuples = list(unique_pairs.itertuples(index=False, name=None))
        # Process each company and extract ESG reports.
        result, no_of_dups = self.extract_esgreports(company_year_tuples)
        
        return result , no_of_dups
