import pandas as pd
import re
import numpy as np

# Load the CSV file
file_path = "labeled_combined_pdfs_2602.csv"
df = pd.read_csv(file_path)

# Define regex patterns for numerical ESG metrics
patterns = {
    "GHG_Emissions": r"(\d+\.?\d*)\s*(?:metric\s*tons|tCO2e)",
    "Energy_Consumption": r"(\d+\.?\d*)\s*(?:MWh|GJ)\b",
    "Water_Consumption": r"(\d+\.?\d*)\s*(?:ML|m³)\b",
    "Waste_Generated": r"(\d+\.?\d*)\s*(?:metric\s*tons|t)\b",
    "Gender_Diversity": r"(\d+)%\s*(?:women|female)",
    "Women_in_Management": r"(\d+)%\s*(?:women|female)\s*in\s*management",
    "Board_Independence": r"(\d+)%\s*(?:independent\s*directors)",
    "Women_on_Board": r"(\d+)%\s*(?:women|female)\s*on\s*board",
}

# Function to extract a numerical metric based on a regex pattern
def extract_metric(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE)
    return float(match.group(1)) if match else np.nan

# Apply regex extraction for numerical metrics
for metric, pattern in patterns.items():
    df[metric] = df["esg_text"].apply(lambda x: extract_metric(str(x), pattern))

# Define indicator metrics (binary: 0 or 1) based on keyword presence
indicators = {
    "Anti_Corruption_Disclosure": ["anti-corruption", "205-1", "205-2", "205-3"],
    "Sustainability_Certifications": ["ISO 45000", "LEED", "BCA Green Building", "ENERGY STAR"],
    "Sustainability_Assurance": ["external assurance", "internal assurance", "no assurance"],
}

def check_indicator(text, keywords):
    return 1 if any(keyword.lower() in text.lower() for keyword in keywords) else 0

# Apply indicator extraction
for indicator, keywords in indicators.items():
    df[indicator] = df["esg_text"].apply(lambda x: check_indicator(str(x), keywords))

# List of all numerical metric columns
numerical_cols = list(patterns.keys())
# List of indicator columns
indicator_cols = list(indicators.keys())

# Normalize numerical metrics to a 0–1 scale (only if at least one value exists)
for col in numerical_cols:
    if df[col].notna().sum() > 0:
        df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

# Calculate ESG pillar scores:
# Each pillar (Environmental, Social, Governance) gets equal weight (33.3% each)
# Environmental (E) metrics
E_metrics = ["GHG_Emissions", "Energy_Consumption", "Water_Consumption", "Waste_Generated"]
# Social (S) metrics – using diversity and management as an example
S_metrics = ["Gender_Diversity", "Women_in_Management"]
# Governance (G) metrics – combining board and indicator metrics
G_metrics = ["Board_Independence", "Women_on_Board",
             "Anti_Corruption_Disclosure", "Sustainability_Certifications", "Sustainability_Assurance"]

# For each row, compute the average for each pillar and then weight by 3.33 (so maximum per pillar is ~3.33)
df["E_Score"] = df[E_metrics].mean(axis=1, skipna=True) * 3.33
df["S_Score"] = df[S_metrics].mean(axis=1, skipna=True) * 3.33
df["G_Score"] = df[G_metrics].mean(axis=1, skipna=True) * 3.33

# Compute final ESG score (out of 10)
df["Final_ESG_Score"] = df[["E_Score", "S_Score", "G_Score"]].sum(axis=1)

# Filter out rows where NO metric data was found
# Here, we keep rows if at least one numerical metric is not NaN OR at least one indicator is 1.
has_num_metric = df[numerical_cols].notna().any(axis=1)
has_indicator = df[indicator_cols].sum(axis=1) > 0
df_metrics_found = df[has_num_metric | has_indicator].copy()

# --- Extract Company Name ---
# This function attempts to extract the company name.
# First, it searches for a pattern like "Company: XYZ".
# If not found, it falls back to taking the first token if it is all uppercase.
def extract_company(text):
    # Try to find "Company: <name>"
    match = re.search(r"Company\s*[:\-]\s*([A-Z][A-Za-z0-9&\s]+)", text)
    if match:
        return match.group(1).strip()
    else:
        tokens = text.split()
        if tokens and tokens[0].isupper():
            return tokens[0]
        else:
            return "Unknown"

df_metrics_found["Company"] = df_metrics_found["esg_text"].apply(lambda x: extract_company(str(x)))

# --- Aggregate by Company ---
# Assuming a company might have multiple rows, compute the average final ESG score per company.
company_scores = df_metrics_found.groupby("Company").agg({
    "E_Score": "mean",
    "S_Score": "mean",
    "G_Score": "mean",
    "Final_ESG_Score": "mean"
}).reset_index()

# Optionally, round scores to 2 decimals
company_scores = company_scores.round(2)

# Save the final aggregated scores per company
output_company_path = "final_company_esg_scores.csv"
company_scores.to_csv(output_company_path, index=False)

