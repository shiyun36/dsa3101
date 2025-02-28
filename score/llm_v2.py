import pandas as pd
import re
import numpy as np
import spacy

# Load spaCy language model
nlp = spacy.load("en_core_web_sm")

# Load the CSV file
file_path = "labeled_combined_pdfs_with_spaces.csv"
df = pd.read_csv(file_path, nrows=2000)

# Define metric information with regex patterns and keywords for NLP fallback
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


def extract_metric(text, metric_key):
    """Try regex extraction; if that fails, use spaCy to find numeric entities near keywords."""
    info = metric_info[metric_key]
    pattern = info["pattern"]
    keywords = info["keywords"]

    # First, try regex extraction.
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except:
            return np.nan
    # If regex fails, use spaCy NER.
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ["CARDINAL", "QUANTITY"]:
            # Check within a window of tokens around the entity for any keyword.
            span_start = max(ent.start - 5, 0)
            span_end = min(ent.end + 5, len(doc))
            window_text = doc[span_start:span_end].text
            if any(keyword.lower() in window_text.lower() for keyword in keywords):
                try:
                    return float(ent.text.replace(',', ''))
                except:
                    continue
    return np.nan


# Apply extraction for each metric column using both regex and NLP.
for metric in metric_info.keys():
    df[metric] = df["esg_text"].apply(lambda x: extract_metric(str(x), metric))

# Define indicator metrics (binary: 0 or 1) based on the presence of keywords.
indicators = {
    "Anti_Corruption_Disclosure": ["anti-corruption", "205-1", "205-2", "205-3"],
    "Sustainability_Certifications": ["ISO 45000", "LEED", "BCA Green Building", "ENERGY STAR"],
    "Sustainability_Assurance": ["external assurance", "internal assurance", "no assurance"],
}


def check_indicator(text, keywords):
    return 1 if any(keyword.lower() in text.lower() for keyword in keywords) else 0


for indicator, keywords in indicators.items():
    df[indicator] = df["esg_text"].apply(lambda x: check_indicator(str(x), keywords))

# List of numerical metric columns and indicator columns.
numerical_cols = list(metric_info.keys())
indicator_cols = list(indicators.keys())

# Normalize numerical metrics (0 to 1) if there is at least one valid value.
for col in numerical_cols:
    if df[col].notna().sum() > 0:
        df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

# Compute ESG pillar scores:
# Environmental (E): GHG, Energy, Water, Waste
E_metrics = ["GHG_Emissions", "Energy_Consumption", "Water_Consumption", "Waste_Generated"]
# Social (S): Gender diversity and Women in management
S_metrics = ["Gender_Diversity", "Women_in_Management"]
# Governance (G): Board metrics and indicator metrics
G_metrics = ["Board_Independence", "Women_on_Board", "Anti_Corruption_Disclosure",
             "Sustainability_Certifications", "Sustainability_Assurance"]

# Each pillar contributes equally (33.3% each) to a final score out of 10.
df["E_Score"] = df[E_metrics].mean(axis=1, skipna=True) * 3.33
df["S_Score"] = df[S_metrics].mean(axis=1, skipna=True) * 3.33
df["G_Score"] = df[G_metrics].mean(axis=1, skipna=True) * 3.33
df["Final_ESG_Score"] = df[["E_Score", "S_Score", "G_Score"]].sum(axis=1)

# Filter rows where any metric data was found.
has_num_metric = df[numerical_cols].notna().any(axis=1)
has_indicator = df[indicator_cols].sum(axis=1) > 0
df_metrics_found = df[has_num_metric | has_indicator].copy()


# --- Company Name Extraction ---
# First, attempt to extract using a "Company:" pattern.
# Otherwise, use spaCy to extract an ORG entity.
def extract_company(text):
    match = re.search(r"Company\s*[:\-]\s*([A-Z][A-Za-z0-9&\s]+)", text)
    if match:
        return match.group(1).strip()
    else:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "ORG":
                return ent.text
        # Fallback: if the first token is uppercase, assume it's the company name.
        tokens = text.split()
        if tokens and tokens[0].isupper():
            return tokens[0]
        return "Unknown"


df_metrics_found["Company"] = df_metrics_found["esg_text"].apply(lambda x: extract_company(str(x)))

# --- Aggregate by Company ---
# If a company appears in multiple rows, average the scores.
company_scores = df_metrics_found.groupby("Company").agg({
    "E_Score": "mean",
    "S_Score": "mean",
    "G_Score": "mean",
    "Final_ESG_Score": "mean"
}).reset_index()

company_scores = company_scores.round(2)

# Save final company-level scores to CSV.
output_company_path = "final_company_esg_scores_nlp.csv"
company_scores.to_csv(output_company_path, index=False)

