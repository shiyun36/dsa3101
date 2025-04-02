import pandas as pd
import time
import requests
import httpx
from bs4 import BeautifulSoup
from openai import OpenAI
import os

# Set your API keys securely (consider using environment variables for production)
API_KEY = os.getenv("OPENAI_API_KEY")  # OpenAI API Key
google_api_key = os.getenv("GOOGLE_API_KEY")  # Google API Key for Custom Search
cse_id = "40a230dc355fa46bf"  # Custom Search Engine ID

#################################################
# Web Search Function (using Google Custom Search)
#################################################
def search_web(query, snippet_length=900):
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

def query_openai_with_search(query):
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

#################################################
# CSV Merging and Parameter Functions
#################################################
def merge_parameters_csv(metrics_file, company_file, year_file, output_file="parameters.csv"):
    """
    Reads three separate CSV files, merges them, and writes the combined DataFrame to a CSV file.
    """
    try:
        df_metrics = pd.read_csv(metrics_file)
        df_company = pd.read_csv(company_file)
        df_year = pd.read_csv(year_file)
    except Exception as e:
        print(f"Error reading one of the CSV files: {e}")
        raise

    # Standardize column names to lowercase.
    df_metrics.columns = df_metrics.columns.str.lower()
    df_company.columns = df_company.columns.str.lower()
    df_year.columns = df_year.columns.str.lower()

    print("Metrics columns:", df_metrics.columns.tolist())
    print("Company columns:", df_company.columns.tolist())
    print("Year columns:", df_year.columns.tolist())

    # Merge based on the number of rows.
    if len(df_metrics) == len(df_company) == len(df_year):
        combined_df = pd.concat([df_metrics, df_company, df_year], axis=1)
    else:
        # Create a cross join if row counts differ.
        df_metrics['key'] = 1
        df_company['key'] = 1
        df_year['key'] = 1
        combined_df = df_metrics.merge(df_company, on='key').merge(df_year, on='key').drop('key', axis=1)

    combined_df.to_csv(output_file, index=False)
    print(f"Combined parameters CSV created successfully at '{output_file}'.")
    return output_file

#################################################
# Modified Query and CSV Output Function
#################################################
def ask_openai_with_template(query_template, parameters_list, output_csv):
    """
    Generates queries from a template using parameters, sends each query to OpenAI using only the internal database context,
    collects responses, and pivots the results so that the output CSV has one row per company/year.
    Each metric from the metrics file becomes a column header with its corresponding answer as the value.
    """
    results = {}
    for params in parameters_list:
        # Convert values to strings and strip whitespace, providing default values if missing.
        company = str(params.get("company", "unknown")).strip()
        year_str = str(params.get("year", "0")).strip()
        metric = str(params.get("metric") or params.get("Metric") or params.get("metrics") or "unknown metric").strip()

        # Debug: Print the row being processed.
        print("Processing row:", params)
        
        # Attempt to convert year to float; if fails, use 0.
        try:
            year_float = float(year_str)
        except ValueError:
            year_float = 0
        
        # If the company is unknown or year is 0, you might decide to skip processing.
        if company.lower() == "unknown" or year_float == 0 or metric.lower() == "unknown metric":
            print("Skipping row due to missing or default values:", params)
            continue

        company_tuple = (company, year_float)
        generic_query = "ESG sustainability report"
        
        # Retrieve internal documents; if not found, the function will attempt to ingest PDFs online.
        internal_results = retrieve_esg_text(company_tuple, generic_query)
        reranked_docs = get_reranked_docs(generic_query, internal_results)
        # Format the query for this specific metric.
        query = query_template.format(company=company, year=year_str, Metric=metric)
        print(f"Querying OpenAI for: {query}")
        response_text = generate_openai_response(query, reranked_docs, company_tuple)["text"]
        
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
    """
    Reads parameters from a CSV file, generates queries via a template,
    collects responses, and saves the responses to a CSV file where each metric is a separate column.
    """
    try:
        df_params = pd.read_csv(parameters_file)
    except Exception as e:
        print(f"Error reading parameters file: {e}")
        raise

    parameters_list = df_params.to_dict('records')
    ask_openai_with_template(query_template, parameters_list, output_csv)

#################################################
# Example Usage
#################################################
if __name__ == "__main__":
    query_template = (
        "Based on the web and your database, determine {metrics} of company {company} for its financial year of {year} from its sustainability reports. Provide a single, clear answer in the format: 'Final Answer: [value]' or an estimate if needed."
    )

    # File paths (ensure these paths exist or update them accordingly)
    metrics_file = "./files/wiki/metrics.csv"
    company_file = "./files/wiki/company.csv"
    year_file = "./files/wiki/year.csv"
    
    # Merge CSV files and generate a combined parameters file.
    parameters_file = merge_parameters_csv(metrics_file, company_file, year_file)

    output_csv = "openai_responses.csv"

    # Generate queries from the parameters file and save OpenAI responses to a CSV file.
    ask_openai_from_file(query_template, parameters_file, output_csv)
