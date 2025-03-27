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

def connect_to_supabase():
    """Establishes connection to Supabase."""
    url = os.getenv("SUPABASE_URL", "your_supabase_url")
    key = os.getenv("SUPABASE_KEY", "your_supabase_key")
    return create_client(url, key)

def fetch_data(supabase):
    """Fetches ESG, stock, and financial data from Supabase."""
    esg_rag = pd.DataFrame(supabase.table("esg_rag_table").select("*").execute().data)
    companies = esg_rag["company"].unique()
    stocks = pd.DataFrame(supabase.table("stocks_table").select("*").eq("company", companies).execute().data)
    roa_roe = pd.DataFrame(supabase.table("roa_roe_table").select("*").execute().data)
    esg_cat = pd.DataFrame(supabase.table("esg_rag_table").select("topic").distinct().execute().data)
    return esg_rag, stocks, roa_roe, esg_cat

def format_data(esg_rag, stocks, roa_roe):
    """Formats data types"""
    roa_roe["date"] = pd.to_datetime(roa_roe["date"], format="%d/%m/%Y")
    roa_roe["year"] = roa_roe["date"].dt.year
    stocks["date"] = pd.to_datetime(stocks["date"], format="%d/%m/%Y")
    stocks["year"] = stocks["date"].dt.year
    stocks["month"] = stocks["date"].dt.month

def transform_data(stocks):
    """Transforms stocks data for financial modeling"""
    prices_year_start = stocks[stocks['month'] == 1].set_index(['company', 'year'])[['close']].rename(columns={'close': 'beginning_price'}).sort_values(by=['company','year'])    
    prices_year_end = stocks[stocks['month'] == 12].set_index(['company', 'year'])[['close']].rename(columns={'close': 'ending_price'}).sort_values(by=['company','year'])  
    stocks_return = prices_year_start.join(prices_year_end).reset_index()
    # Compute annual linear return
    stocks_return['stock growth'] = (stocks_return['ending_price'] - stocks_return['beginning_price']) / stocks_return['beginning_price']
    return stocks_return

def clean_data(esg_rag, stocks, roa_roe):
    """Performs data cleaning, handling missing values, and ensuring data consistency."""
    esg_rag['final_score'] = esg_rag['final_score'].apply(lambda x: np.nan if x < 0 or x > 1 else x)
    esg_rag.dropna(inplace=True)
    stocks.dropna(subset=['stock growth'], inplace=True)
    roa_roe.dropna(subset=['roa', 'roe'], inplace=True)
    return esg_rag, stocks, roa_roe

def get_esg_categories(supabase):
    """Fetch distinct ESG topics from the Supabase table."""
    esg_cat_sql = (
        supabase.table("esg_rag_table")
        .select("topic")
        .distinct()
        .execute()
    )
    esg_cat = pd.DataFrame(esg_cat_sql.data)
    return esg_cat.tolist()

def compute_esg_scores(esg_rag, esg_categories):
    """Compute ESG component scores and overall ESG score."""
    env_metrics = esg_categories[:4]
    social_metrics = esg_categories[4:15]
    governance_metrics = esg_categories[15:]
    
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
    return esg_wide


def merge_financial_esg_data(roa_roe, esg_wide, stocks_return):
    """Merge financial and ESG data and save to CSV."""
    df = roa_roe.merge(
        esg_wide[["company", "year", "environmental_score", "social_score", "governance_score", "overall_esg_score"]], 
        on=["company", "year"], 
        how="inner"
    )
    df = df.merge(stocks_return[["company", "year", "stock growth"]], on=["company", "year"])
    return df

def build_financial_model(df):
    """Builds and trains a regression model for roa, roe and stock prediction."""
    # Define independent variable
    X = df["overall_esg_score"]
    X = sm.add_constant(X)  # Add intercept
    
    # Dependent variables
    y_roa = df["roa"]
    y_roe = df["roe"]
    y_stock = df["stock growth"]
    
    # Fit regression models
    model_roa = sm.OLS(y_roa, X).fit()
    model_roe = sm.OLS(y_roe, X).fit()
    model_stock = sm.OLS(y_stock, X).fit()

    return model_roa, model_roe, model_stock    

def run():
    """Main function to execute the full pipeline."""
    supabase = connect_to_supabase()
    esg_rag, stocks, roa_roe, esg_cat = fetch_data(supabase)
    stocks = transform_data(stocks)
    esg_rag, stocks, roa_roe = clean_data(esg_rag, stocks, roa_roe)
    esg_categories = get_esg_categories(supabase)
    # Compute ESG scores
    esg_wide = compute_esg_scores(esg_rag, esg_categories)
    # Merge data
    df = merge_financial_esg_data(roa_roe, esg_wide, stocks_return)
    model = build_financial_model(stocks, roa_roe) # change this line to use df
    print(model.summary())
    
    
if __name__ == "__main__":
    run()