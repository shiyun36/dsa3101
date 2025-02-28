import pandas as pd
import re
import numpy as np
import spacy
import math

# Load spaCy language model
nlp = spacy.load("en_core_web_sm")

# --- Step 1: Read CSV and Group Rows by Company ---
# The CSV has a column "esg_text". A blank "esg_text" indicates a new company.
file_path = "labeled_combined_pdfs_with_spaces.csv"
df = pd.read_csv(file_path, nrows=2000)

company_texts = []
current_company_text = ""
for index, row in df.iterrows():
    text = str(row['esg_text']).strip()
    if text == "":  # blank row indicates new company
        if current_company_text:
            company_texts.append(current_company_text.strip())
            current_company_text = ""
    else:
        current_company_text += " " + text
# Append last company if any remains
if current_company_text.strip():
    company_texts.append(current_company_text.strip())

# --- Step 2: Define Metric Extraction Methods ---
# Define numerical metrics with regex patterns and keywords for NLP fallback.
metric_info = {
    "GHG_Emissions": {
        "pattern": r"(\d+\.?\d*)\s*(?:metric\s*tons|tCO2e)",
        "keywords": ["GHG", "CO2", "emissions"]
    },
    "Energy_Consumption": {
        "pattern": r"(\d+\.?\d*)\s*(?:MWh|GJ)\b",
        "keywords": ["energy", "MWh", "GJ", "consumption"]
    },
    "Water_Consumption": {
        "pattern": r"(\d+\.?\d*)\s*(?:ML|m³)\b",
        "keywords": ["water", "ML", "m³", "consumption"]
    },
    "Waste_Generated": {
        "pattern": r"(\d+\.?\d*)\s*(?:metric\s*tons|t)\b",
        "keywords": ["waste", "tons", "waste generated"]
    },
    "Gender_Diversity": {
        "pattern": r"(\d+)%\s*(?:women|female)",
        "keywords": ["gender", "diversity", "female"]
    },
    "Women_in_Management": {
        "pattern": r"(\d+)%\s*(?:women|female)\s*in\s*management",
        "keywords": ["women", "management", "female", "senior management"]
    },
    "Board_Independence": {
        "pattern": r"(\d+)%\s*(?:independent\s*directors)",
        "keywords": ["board", "independent", "directors"]
    },
    "Women_on_Board": {
        "pattern": r"(\d+)%\s*(?:women|female)\s*on\s*board",
        "keywords": ["women", "board", "female"]
    },
}

# Define indicator metrics (binary: 0 or 1)
indicators = {
    "Anti_Corruption_Disclosure": ["anti-corruption", "205-1", "205-2", "205-3"],
    "Sustainability_Certifications": ["ISO 45000", "LEED", "BCA Green Building", "ENERGY STAR"],
    "Sustainability_Assurance": ["external assurance", "internal assurance", "no assurance"],
}


def extract_metric(text, metric_key):
    """
    Extract a numerical metric using regex. If that fails,
    use spaCy NER to find a number near related keywords.
    """
    info = metric_info[metric_key]
    pattern = info["pattern"]
    keywords = info["keywords"]

    # Attempt regex extraction
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except Exception:
            return np.nan
    # Fallback: use spaCy NER
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ["CARDINAL", "QUANTITY"]:
            span_start = max(ent.start - 5, 0)
            span_end = min(ent.end + 5, len(doc))
            window_text = doc[span_start:span_end].text
            if any(keyword.lower() in window_text.lower() for keyword in keywords):
                try:
                    return float(ent.text.replace(',', ''))
                except Exception:
                    continue
    return np.nan


def check_indicator(text, keywords):
    """Return 1 if any of the keywords is found in the text; otherwise, 0."""
    return 1 if any(keyword.lower() in text.lower() for keyword in keywords) else 0


# --- Step 3: Process Each Company's Text to Extract Metrics ---
company_results = []
for comp_text in company_texts:
    metrics = {}
    # Extract numerical/percentage metrics using combined NLP + regex.
    for metric in metric_info.keys():
        metrics[metric] = extract_metric(comp_text, metric)
    # Extract indicator metrics.
    for ind in indicators.keys():
        metrics[ind] = check_indicator(comp_text, indicators[ind])
    # Only include company if at least one metric is found.
    numerical_found = any(not np.isnan(metrics[m]) for m in metric_info.keys())
    indicator_found = any(metrics[ind] == 1 for ind in indicators.keys())
    if numerical_found or indicator_found:
        # Use spaCy to extract a company name (first ORG found) or default to "Unknown"
        doc = nlp(comp_text)
        company_name = None
        for ent in doc.ents:
            if ent.label_ == "ORG":
                company_name = ent.text
                break
        if company_name is None:
            company_name = "Unknown"
        metrics["Company"] = company_name
        company_results.append(metrics)

# --- Step 4: Normalize Numerical Metrics (0 to 1) ---
for metric in metric_info.keys():
    values = [d[metric] for d in company_results if not math.isnan(d[metric])]
    if values:
        min_val = min(values)
        max_val = max(values)
        for d in company_results:
            if not math.isnan(d[metric]):
                if max_val == min_val:
                    d[metric] = 1.0
                else:
                    d[metric] = (d[metric] - min_val) / (max_val - min_val)

# --- Step 5: Calculate ESG Scores ---
# Define pillars:
E_metrics = ["GHG_Emissions", "Energy_Consumption", "Water_Consumption", "Waste_Generated"]
S_metrics = ["Gender_Diversity", "Women_in_Management"]
G_metrics = ["Board_Independence", "Women_on_Board", "Anti_Corruption_Disclosure",
             "Sustainability_Certifications", "Sustainability_Assurance"]


def safe_mean(values):
    valid = [v for v in values if not math.isnan(v)]
    return sum(valid) / len(valid) if valid else np.nan


for d in company_results:
    E_avg = safe_mean([d.get(m, np.nan) for m in E_metrics])
    S_avg = safe_mean([d.get(m, np.nan) for m in S_metrics])
    G_avg = safe_mean([d.get(m, np.nan) for m in G_metrics])
    d["E_Score"] = E_avg * 3.33 if not np.isnan(E_avg) else 0
    d["S_Score"] = S_avg * 3.33 if not np.isnan(S_avg) else 0
    d["G_Score"] = G_avg * 3.33 if not np.isnan(G_avg) else 0
    d["Final_ESG_Score"] = d["E_Score"] + d["S_Score"] + d["G_Score"]

# --- Step 6: Build DataFrame and Insert Blank Rows Between Companies ---
result_df = pd.DataFrame(company_results)
# Ensure "Company" is the first column.
cols = result_df.columns.tolist()
cols.insert(0, cols.pop(cols.index("Company")))
result_df = result_df[cols]

# Insert blank rows between each company's row in the output.
rows_with_blanks = []
for idx, row in result_df.iterrows():
    rows_with_blanks.append(row.to_dict())  # convert Series to dict
    blank_row = {col: "" for col in result_df.columns}
    rows_with_blanks.append(blank_row)
final_df = pd.DataFrame(rows_with_blanks)

# --- Step 7: Save the Final Output ---
output_path = "final_company_esg_scores_nlp_with_blanks.csv"
final_df.to_csv(output_path, index=False)
print("Output saved to:", output_path)
