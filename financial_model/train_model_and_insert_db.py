#$ pip install httpx[http2]

import os
from supabase import create_client
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from sklearn.feature_selection import RFE
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
from collections import Counter
from scripts.db_insert_model_lr import insert_model_lr

def connect_to_supabase():
    """Establishes connection to Supabase."""
    try:
        url = os.getenv("SUPABASE_URL", "your_supabase_url")
        key = os.getenv("SUPABASE_KEY", "your_supabase_key")
        if not url or not key:
            raise ValueError("Supabase URL or key is missing.")
        return create_client(url, key)
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        return None

def fetch_data(supabase):
    """Fetches ESG, stock, and financial data from Supabase."""
    try:
        esg_rag = pd.DataFrame(supabase.table("esg_rag_table").select("*").execute().data)
        stocks = pd.DataFrame(supabase.table("stocks_table").select("*").execute().data)
        roa_roe = pd.DataFrame(supabase.table("roa_roe_table").select("*").execute().data)
        return esg_rag, stocks, roa_roe
    except Exception as e:
        print(f"Error fetching data from Supabase: {e}")
        return None, None, None#, None
        
def format_data(esg_rag, stocks, roa_roe):
    """Formats data types"""
    try:
        roa_roe["date"] = pd.to_datetime(roa_roe["date"], format="%Y-%m-%d")
        roa_roe["year"] = roa_roe["date"].dt.year
        stocks["date"] = pd.to_datetime(stocks["date"], format="%Y-%m-%d")
        stocks["year"] = stocks["date"].dt.year
        stocks["month"] = stocks["date"].dt.month
    except Exception as e:
        print(f"Error formatting data: {e}")

def transform_data(stocks):
    """Transforms stocks data for financial modeling"""
    try:
        prices_year_start = stocks[stocks['month'] == 1].set_index(['company', 'year'])[['close']].rename(columns={'close': 'beginning_price'}).sort_values(by=['company','year'])    
        prices_year_end = stocks[stocks['month'] == 12].set_index(['company', 'year'])[['close']].rename(columns={'close': 'ending_price'}).sort_values(by=['company','year'])  
        stocks_return = prices_year_start.join(prices_year_end).reset_index()
        stocks_return['stock growth'] = (stocks_return['ending_price'] - stocks_return['beginning_price']) / stocks_return['beginning_price']
        return stocks_return
    except Exception as e:
        print(f"Error transforming data: {e}")
        return None


def clean_data(esg_rag, stocks, roa_roe):
    """Performs data cleaning, handling missing values, and ensuring data consistency."""
    try:
        esg_rag['final_score'] = esg_rag['final_score'].apply(lambda x: np.nan if x < 0 or x > 1 else x)
        stocks.dropna(subset=['stock growth'], inplace=True)
        roa_roe.dropna(subset=['roa', 'roe'], inplace=True)
        return esg_rag, stocks, roa_roe
    except Exception as e:
        print(f"Error cleaning data: {e}")
        return esg_rag, stocks, roa_roe

def compute_esg_scores(esg_rag):
    """Compute ESG component scores and overall ESG score."""
    try:
        env_metrics = ["Total Greenhouse Gas Emissions", "Total Energy consumption", "Total Waste Generated", "Total Water Consumption"]
        social_metrics = ["Current Employees by Gender", "Employee Turnover rate by Gender", "New Hires by Gender", "Current Employees by Age Groups", "New employee hires by age group", "Total turnover rate", "Average Training Hours per Employee", "Fatalities", "High-consequence injuries", "Recordable injuries", "Number of Recordable Work-related Ill Health Cases"]
        governance_metrics = ["Board Independence", "Women on the Board", "Women in Management", "Anti-corruption disclosures", "Anti-Corruption Training for Employees", "Certification", "Alignment with frameworks and disclosure practices", "Assurance of sustainability report"]
        
        esg_wide = esg_rag.pivot_table(
            index=["company", "year"], 
            columns="topic", 
            values="final_score", 
            aggfunc="first"
        ).reset_index()
        
        esg_wide["environmental_score"] = esg_wide[env_metrics].mean(axis=1)
        esg_wide["social_score"] = esg_wide[social_metrics].mean(axis=1)
        esg_wide["governance_score"] = esg_wide[governance_metrics].mean(axis=1)
        
        esg_wide["overall_esg_score"] = (
            esg_wide["environmental_score"] * 3.33 +
            esg_wide["social_score"] * 3.33 +
            esg_wide["governance_score"] * 3.33
        )
        esg_overall_score = esg_wide
        esg_overall_score.dropna(subset=['overall_esg_score'], inplace=True)
        return esg_overall_score
    except Exception as e:
        print(f"Error computing ESG scores: {e}")
        return None

def merge_financial_esg_data(roa_roe, esg_overall_score, stocks_return):
    """Merge financial and ESG data."""
    try:
        df = roa_roe.merge(
            esg_overall_score[["company", "year", "environmental_score", "social_score", "governance_score", "overall_esg_score"]], 
            on=["company", "year"], 
            how="inner"
        )
        df = df.merge(stocks_return[["company", "year", "stock growth"]], on=["company", "year"])
        return df
    except Exception as e:
        print(f"Error merging financial and ESG data: {e}")
        return None

# Function to extract relevant variables from the dataframe
def extract_variables(df):
    """Extracts independent and dependent variables for the model."""
    try:
        # Independent variable
        X = df["overall_esg_score"]
        X = sm.add_constant(X)  # Add intercept
        
        # Dependent variables
        y_roa = df["roa"].tolist()
        y_roe = df["roe"].tolist()
        y_stock = df["stock growth"].tolist()
        
        return X, y_roa, y_roe, y_stock
    except Exception as e:
        print(f"Error extracting variables: {e}")
        return None, None, None, None
    
# Function to build the financial regression models
def build_financial_model(X, y_roa, y_roe, y_stock):
    """Builds the regression models for ROA, ROE, and Stock Growth."""
    try:
        # Fit models for ROA, ROE, and Stock Growth
        model_roa = LinearRegression().fit(X, y_roa)
        model_roe = LinearRegression().fit(X, y_roe)
        model_stock = LinearRegression().fit(X, y_stock)
        return model_roa, model_roe, model_stock
    except Exception as e:
        print(f"Error building models: {e}")
        return None, None, None

# Function to make predictions for ROA, ROE, and Stock Growth
def predict_values(model_roa, model_roe, model_stock, X):
    """Make predictions for ROA, ROE, and Stock Growth using the models."""
    try:
        y_roa_pred = model_roa.predict(X)
        y_roe_pred = model_roe.predict(X)
        y_stock_pred = model_stock.predict(X)
        return y_roa_pred, y_roe_pred, y_stock_pred
    except Exception as e:
        print(f"Error making predictions: {e}")
        return None, None, None

def prep_model():
    """Main function to prepare the data for PowerBI."""
    supabase = connect_to_supabase()
    if supabase is None:
        print("Failed to connect to Supabase.")
        return
    
    esg_rag, stocks, roa_roe = fetch_data(supabase)
    if esg_rag is None or stocks is None or roa_roe is None:
        print("Failed to fetch data.")
        return
    
    format_data(esg_rag, stocks, roa_roe)
    stocks_return = transform_data(stocks)
    esg_rag, stocks_return, roa_roe = clean_data(esg_rag, stocks_return, roa_roe)
    esg_overall_score = compute_esg_scores(esg_rag)
    df = merge_financial_esg_data(roa_roe, esg_overall_score, stocks_return)
    return df, esg_rag, roa_roe, esg_overall_score, stocks_return

def prep_rfe(esg_rag, roa_roe, stocks_return):
    try:
        esg_wide = esg_rag.pivot_table(
            index=["company", "year"], 
            columns="topic", 
            values="final_score", 
            aggfunc="first"
        ).reset_index()
        
        df_features = roa_roe.merge(esg_wide, on=["company", "year"], how="inner") \
                              .merge(stocks_return[["company", "year", "stock growth"]], on=["company", "year"]) \
                              .dropna()

        features = df_features.drop(columns=['roa', 'roe', 'stock growth', 'company', 'year', 'date', 'Certification'])
        targets = ['roa', 'roe', 'stock growth']
        return df_features, features, targets
    except Exception as e:
        print(f"Error preparing RFE: {e}")
        return None, None, None

def rfe(df_features, features, targets):
    """Get Top 5 ESG Metrics that best predict ROA, ROE, Stock Prices in ranked order."""
    try:
        # Store ranked features per target
        top_features_rfe = {}

        for target in targets:
            model = LinearRegression()
            rfe_selector = RFE(model, n_features_to_select=5)
            rfe_selector.fit(features, df_features[target])

            # Get ordered list of selected features based on ranking_
            selected_features = [
                feature for _, feature in sorted(zip(rfe_selector.ranking_, features.columns))
            ][:5]  # Only take the top 5

            top_features_rfe[target] = selected_features
        
        # Get overall top 5 most frequently selected features across targets
        all_selected_features = sum(top_features_rfe.values(), [])
        top_5_features = [feature for feature, _ in Counter(all_selected_features).most_common(5)]

        # Convert to DataFrame (long format)
        rows = []
        for target, feature_list in top_features_rfe.items():
            for rank, feature in enumerate(feature_list, start=1):
                rows.append({"Target Variable": target, "Feature": feature, "Rank": rank})
        
        for rank, feature in enumerate(top_5_features, start=1):
            rows.append({"Target Variable": "Overall", "Feature": feature, "Rank": rank})
        
        df_rfe = pd.DataFrame(rows)
        
        return df_rfe
    except Exception as e:
        print(f"Error performing RFE: {e}")
        return None

# Main function to run the entire analysis
def run_analysis(df):
    """Runs the entire regression analysis and returns the dataframe with predictions."""
    try:
        # Extract variables
        X, y_roa, y_roe, y_stock = extract_variables(df)
        if X is None or y_roa is None or y_roe is None or y_stock is None:
            print("Error: Unable to extract variables.")
            return None

        # Build the regression models
        model_roa, model_roe, model_stock = build_financial_model(X, y_roa, y_roe, y_stock)
        if model_roa is None or model_roe is None or model_stock is None:
            print("Error: Unable to build models.")
            return None

        # Make predictions
        y_roa_pred, y_roe_pred, y_stock_pred = predict_values(model_roa, model_roe, model_stock, X)
        if y_roa_pred is None or y_roe_pred is None or y_stock_pred is None:
            print("Error: Unable to make predictions.")
            return None

        # Create a new dataframe for Power BI
        results_df = pd.DataFrame({
            'ESG_Score': X['overall_esg_score'],
            'ROA_Actual': y_roa,
            'ROA_Predicted': y_roa_pred,
            'ROE_Actual': y_roe,
            'ROE_Predicted': y_roe_pred,
            'Stock_Growth_Actual': y_stock,
            'Stock_Growth_Predicted': y_stock_pred
        })

        return results_df
    except Exception as e:
        print(f"Error running analysis: {e}")
        return None

# Main execution
def main():
    df, esg_rag, roa_roe, esg_overall_score, stocks_return = prep_model()
    df_features, features, targets = prep_rfe(esg_rag, roa_roe, stocks_return)

    # Run the analysis
    results_df = run_analysis(df)
    df_rfe = rfe(df_features, features, targets)

    # Check if results are generated
    if results_df is not None or df_rfe is not None:
        # Display the first few rows of the dataframe
        print(results_df.head())
        print(df_rfe)
        insert_model_lr(results_df, df_rfe)
        return results_df, df_rfe  # This will be used in Power BI

# Call main function
if __name__ == "__main__":
    main()