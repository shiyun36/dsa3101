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
### if u got strong gpu, average laptop cpu takes too long *cough* mac book users
torch.set_default_device("cpu")

if torch.cuda.is_available():
    torch.set_default_device("cuda")
    print("running on cuda")

from sklearn.metrics.pairwise import cosine_similarity
import sys
import httpx
import logging
API_KEY = ""
from openai import OpenAI
##### DB STUFF #####

def company_year_exists(company, year):
    """Check dup companies"""

    client = chromadb.PersistentClient(path="./chromadb_1003")  # Stores DB in ./chroma_db
    collection = client.get_or_create_collection(name="dsa3101")
    results = collection.query(
        query_texts=[""],  # Empty query text since we're filtering solely by metadata
        n_results=1,
        where={
    "$and": [
        {"company": company},
        {"year": int(year)}
    ]

}

    )
    # Check if any document was returned
    if results.get("documents") and results["documents"][0]:
        return True
    return False

def add_documents_from_csv(file_path): #leaving this here but not in use for now
    """Add docs from csv to chromadb"""
    client = chromadb.PersistentClient(path="./chromadb_1003")  # Stores DB in ./chroma_db
    collection = client.get_or_create_collection(name="dsa3101")
    try:
        df = pd.read_csv(file_path)
    except pd.errors.ParserError as e:
        logging.error(f"Parser error while loading {file_path}: {e}")
        return
    except Exception as e:
        logging.error(f"Failed to load {file_path}: {e}")
        return
    
    # Capture the starting document count to keep doc_ids consistent
    groups = df.groupby(["company", "year"])

    # Process each group only once
    for (company, year), group_df in tqdm(groups, total=len(groups), desc="Processing groups", unit="group", ncols=100):
        if company_year_exists(company, int(year)):
            print(f"Group for {company} ({year}) already exists. Skipping all documents for this group.")
            continue

        # Capture starting count for unique doc_ids for this group
        starting_count = collection.count()
        # Add all rows in the group
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
def add_documents_from_df(df):
    """
    Add df that has 'esg_text', 'company', 'year', 'industry', 'country'.
    """
    client = chromadb.PersistentClient(path="./chromadb_1003")
    collection = client.get_or_create_collection(name="dsa3101")

    # Group by (company, year)
    groups = df.groupby(["company", "year"])

    # Process each group only once
    for (company, year), group_df in tqdm(groups, total=len(groups), desc="Processing groups", unit="group", ncols=100):
        if company_year_exists(company, year):
            print(f"Group for {company} ({year}) already exists. Skipping all documents for this group.")
            continue

        # Capture the starting count for unique doc_ids for this group
        starting_count = collection.count()
        # Add all rows in the group
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

def generate_openai_response(query, reranked_docs, company_tuple):
    """Retrieve context from ChromaDB and generate an answer using DeepSeek."""

    llm_openai = OpenAI(
    api_key=API_KEY,
    http_client= httpx.Client())
    
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
            response = llm_openai.chat.completions.create(
                model="gpt-3.5-turbo",  # or your preferred model
                messages=[
                    {"role": "assistant", "content": "You are an expert in ESG analysis looking through several documents"},
                    { "role": "user", "content": prompt},
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

def rerank_documents(query, retrieved_docs):
    reranker_model_name = "BAAI/bge-reranker-base"
    reranker_tokenizer = AutoTokenizer.from_pretrained(reranker_model_name)
    reranker_model = AutoModelForSequenceClassification.from_pretrained(reranker_model_name)

    if not retrieved_docs:
        return []

    # tokenise the query? = solve the ranking
    query_inputs = reranker_tokenizer(query, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        query_outputs = reranker_model(**query_inputs,output_hidden_states=True)
    # For simplicity, use the [CLS] token (first token) as the query embedding.
    query_embedding = query_outputs.hidden_states[-1][:, 0]
    
    doc_inputs = reranker_tokenizer(retrieved_docs, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        doc_outputs = reranker_model(**doc_inputs,output_hidden_states=True)
    # Use the [CLS] token embedding for each document.
    doc_embeddings = doc_outputs.hidden_states[-1][:, 0]

    # Compute relevance scores
    similarities = F.cosine_similarity(query_embedding, doc_embeddings, dim=-1)  # shape: (num_docs,)

    # Sort retrieved docs by relevance score (descending order)
    sorted_indices = similarities.argsort(descending=True)
    reranked_docs = [retrieved_docs[i] for i in sorted_indices.tolist()]
    return reranked_docs

def retrieve_company_metadata(company_tuple):
    """
    Query the collection to retrieve metadata for a given company.
    Expects company_tuple to be (company_name, year).
    """
    chroma_client = chromadb.PersistentClient(path="./chromadb_1003")
    collection = chroma_client.get_or_create_collection(name="dsa3101")
    results = collection.query(
        query_texts=[""],  # no text query; we use metadata filtering only
        n_results=1,
        where={"$and": [{"company": company_tuple[0]}, {"year": int(company_tuple[1])}]}
    )
    if not results.get("documents") or not results["documents"][0]:
        print(f"Company '{company_tuple[0]}' for year '{company_tuple[1]}' is not in the database. Exiting.")
        sys.exit(1)

    # Assumes metadata is stored along with the document. For example:
    # metadatas: [[{"company": "DBS", "year": 2023.0, "country": "Singapore", "industry": "Finance"}]]
    metadata = results["metadatas"][0][0]
    if "country" not in metadata or "industry" not in metadata:
        print(f"Metadata for {company_tuple[0]} is missing 'country' or 'industry' fields. Exiting.")
        sys.exit(1)
    return metadata

def retrieve_esg_text(company_tuple, query):
    """
    Retrieve ESG text from ChromaDB for a company given a specific query.
    """
    chroma_client = chromadb.PersistentClient(path="./chromadb_1003")
    collection = chroma_client.get_or_create_collection(name="dsa3101")
    results = collection.query(
        query_texts=[query],
        n_results=15,
        where={"$and": [{"company": company_tuple[0]}, {"year": int(company_tuple[1])}]}
    )
    if not results.get("documents") or not results["documents"][0]:
        print(f"Company '{company_tuple[0]}' for year '{int(company_tuple[1])}' is not in the database. Exiting.")
        sys.exit(1)
    return results

def get_reranked_docs(query, results):
    retrieved_docs = [doc for doc in results["documents"][0]]
    reranked_docs = rerank_documents(query, retrieved_docs)
    return reranked_docs

def extract_values(query, results,company_tuple):
    reranked_docs = get_reranked_docs(query, results)
    response = generate_openai_response(query, reranked_docs,company_tuple)
    return response

def compute_linear_score(extracted_values, scoring_query, company_tuple):
    final_answer_generator = 'Return your answer as: "Final Answer: X" (where X is a numeric or clearly defined answer)'
    score = generate_openai_response(scoring_query + final_answer_generator, str(extracted_values),company_tuple)
    return score

def extract_absolute_score(score):
    matches = re.findall(r"(?:Final\s*Answer|Answer).*?([-+]?\d*\.?\d+)(?:\s*\%\.)?", str(score), re.DOTALL)
    return float(matches[-1]) if matches else "N/A"


def process_company(company_tuple):

    metadata = retrieve_company_metadata(company_tuple)
    country = metadata.get("country", "").strip().lower()
    industry = metadata.get("industry", "").strip().lower()
    
    # Choose JSON query file and CSV file based on country and industry.
    if country == "singapore":
        if industry == "finance":
            query_file = "../files/scoring_queries/sg_bank_query.json"
            csv_file = "../notebooks/extractValues/sg_finance_score.csv"
        elif industry == "health":
            query_file = "../files/scoring_queries/sg_healthcare_query.json"
            csv_file = "../notesbooks/extractValues/sg_healthcare_score.csv"
        else:
            print(f"Unsupported industry '{industry}' for country '{country}'. Exiting.")
            sys.exit(1)
    else:
        print(f"Unsupported country '{country}'. Exiting.")
        sys.exit(1)

    # Load the ESG metrics from the JSON file
    try:
        with open(query_file, "r") as file:
            esg_metrics = json.load(file)
    except Exception as e:
        print(f"Error loading JSON file '{query_file}': {e}")
        sys.exit(1)
        
    # Prepare DataFrame headers based on the metrics in the JSON file.
    headers = []
    for item in esg_metrics:
        metric_name = list(item.keys())[0]  
        headers.append(metric_name)         
        headers.append(f"{metric_name}_numScore")  
    df_columns = ["Company", "Year", "Industry", "Country"] + headers  # one column per ESG metric
    
    # Load existing CSV for this combination if it exists
    if os.path.exists(csv_file):
        df_existing = pd.read_csv(csv_file)
        existing_companies = set(map(tuple, df_existing[['Company','Year',"Industry","Country"]].values.tolist()))
    else:
        print("Path to CSV file does not exist. Creating a new one.")
        df_existing = pd.DataFrame(columns=df_columns)
        existing_companies = set()
    
    # Skip if company has already been processed for this CSV
    if tuple(company_tuple) + (industry,country) in existing_companies:
        print(f"Company '{company_tuple[0]}' for year '{company_tuple[1]}' already processed; skipping.")
        return None, csv_file, df_columns

    row_data = {"Company": company_tuple[0], "Year": company_tuple[1], "Industry": industry, "Country": country}
    
    # Process each ESG metric defined in the JSON file.
    for metric_item in esg_metrics:
        for metric, details in metric_item.items():
            metric_name = metric
            query = details["value_query"]
            scoring_thresholds = details["scoring_query"]

            # Retrieve ESG text using the query.
            retrieved_text = retrieve_esg_text(company_tuple, query)
            # Extract values using DeepSeek (or your equivalent method).
            extracted_values = extract_values(query, retrieved_text,company_tuple)
            # Compute the linear score.
            score = compute_linear_score(extracted_values, scoring_thresholds,company_tuple)
            
            row_data[metric_name] = {"extracted_values": extracted_values, "score": score}
            row_data[metric_name + '_numScore'] = extract_absolute_score(score)

    return row_data, csv_file, df_columns




# Use a dictionary to group new rows by the target CSV file.
def extract_esgreports(companies):
    
    final_dataframes = {}
    new_rows = {}

    for company_tuple in companies:
        # process_company is assumed to be defined elsewhere
        row_data, csv_file, df_columns = process_company(company_tuple)

        # If no row_data, skip
        if row_data is None:
            print("No new data to add.")
            continue

        # If this CSV hasn't been seen yet, initialize a new entry
        if csv_file not in new_rows:
            new_rows[csv_file] = {"rows": [], "columns": df_columns}

        # Add the row data to our in-memory collection
        new_rows[csv_file]["rows"].append(row_data)



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

        print(f"Added {len(data['rows'])} new companies to {csv_file}.")
    
    print("final_df: " + str(final_df))
    print("final_dataframes: " + str(final_dataframes))

    return final_df


companies = [
    ("DBS", 2023.0),
    ("UOBGROUP", 2023.0),
    ("OCBC", 2023.0),
    ("ECONHEALTHCARE", 2024.0),
    ("FULLERTONHEALTH", 2023.0),
    ("HEALTHMEDICAL", 2022.0),
    ("HSA", 2023.0)
]

def rag_main(new_companies_df):
    if not isinstance(new_companies_df, pd.DataFrame):
        raise TypeError(f"Input must be a pandas DataFrame, got {type(new_companies_df)} instead.")
    add_documents_from_df(new_companies_df)

    # Extract just the two columns of interest
    subset = new_companies_df[['company', 'year']]

    # Drop duplicate rows
    unique_pairs = subset.drop_duplicates()
    unique_pairs['year'] = unique_pairs['year'].astype(int)
    # Convert each row to a tuple if needed:
    company_year_tuples = list(unique_pairs.itertuples(index=False, name=None))

    df = extract_esgreports(company_year_tuples)
    print("rag_main function: " + str(df))
    return df


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python myscript.py <input_csv>")
        sys.exit(1)

    input_df = sys.argv[1]

    rag_main(input_df)