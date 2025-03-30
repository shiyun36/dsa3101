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

def connect_to_supabase():
    """Establishes connection to Supabase."""
    try:
        url = os.getenv("SUPABASE_URL", "your_supabase_url") # Replace with your url
        key = os.getenv("SUPABASE_KEY", "your_supabase_key") # Replace with your key
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
        esg_cat = pd.DataFrame(supabase.table("esg_rag_table").select("topic").execute().data)
        esg_cat = esg_cat["topic"].unique().tolist()
        return esg_rag, stocks, roa_roe, esg_cat
    except Exception as e:
        print(f"Error fetching data from Supabase: {e}")
        return None, None, None, None
        
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

def compute_esg_scores(esg_rag, esg_cat):
    """Compute ESG component scores and overall ESG score."""
    try:
        env_metrics = esg_cat[:4]
        social_metrics = esg_cat[4:15]
        governance_metrics = esg_cat[15:]
        
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
        return None, None

def rfe(df_features, features, targets):
    """Get Top 5 ESG Metrics that best predict ROA, ROE, Stock Prices."""
    try:
        top_features_rfe = {
            target: np.array(features.columns)[RFE(LinearRegression(), n_features_to_select=5).fit(features, df_features[target]).support_].tolist()
            for target in targets
        }
        print("Top 5 features per target variable using RFE:")
        for target, features in top_features_rfe.items():
            print(f"{target}: {features}")
        
        all_selected_features = sum(top_features_rfe.values(), [])
        top_5_features = [feature for feature, _ in Counter(all_selected_features).most_common(5)]
        
        print("\nTop 5 Features Across All Targets:\n", top_5_features)
        return top_features_rfe, top_5_features
    except Exception as e:
        print(f"Error performing RFE: {e}")
        return None, None

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

def build_financial_model(X, y_roa, y_roe, y_stock):
    """Builds and trains regression models for ROA, ROE, and stock growth."""
    try:
        model_roa = sm.OLS(y_roa, X).fit()
        model_roe = sm.OLS(y_roe, X).fit()
        model_stock = sm.OLS(y_stock, X).fit()

        return model_roa, model_roe, model_stock
    except Exception as e:
        print(f"Error building financial models: {e}")
        return None, None, None
############
def predict_values(model_roa, model_roe, model_stock, X):
    """Makes predictions using the trained models."""
    try:
        y_roa_pred = model_roa.predict(X)
        y_roe_pred = model_roe.predict(X)
        y_stock_pred = model_stock.predict(X)

        return y_roa_pred, y_roe_pred, y_stock_pred
    except Exception as e:
        print(f"Error making predictions: {e}")
        return None, None, None

def plot_financial(y_actual, y_pred, residuals, title, xlabel, ylabel):
    """Generates a scatter plot for predicted vs actual and residual plot."""
    try:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Predicted vs Actual plot
        axes[0].scatter(y_actual, y_pred, color='blue', label='Data')
        axes[0].plot([min(y_actual), max(y_actual)], [min(y_actual), max(y_actual)], color='red', linestyle='--', label='Ideal fit')
        axes[0].set_title(f'{title}: Predicted vs Actual')
        axes[0].set_xlabel(xlabel)
        axes[0].set_ylabel(ylabel)
        axes[0].legend()

        # Residual plot
        axes[1].scatter(y_pred, residuals, color='blue')
        axes[1].axhline(0, color='black', linestyle='--')
        axes[1].set_title(f'{title} Residuals')
        axes[1].set_xlabel(f'Predicted {xlabel}')
        axes[1].set_ylabel('Residuals')

        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Error plotting financial data: {e}")

def plot_all_results(y_roa, y_roa_pred, model_roa, y_roe, y_roe_pred, model_roe, y_stock, y_stock_pred, model_stock):
    """Plots predicted vs actual and residuals for ROA, ROE, and Stock Growth."""
    plot_financial(y_roa, y_roa_pred, model_roa.resid, "ROA Model", "Actual ROA", "Predicted ROA")
    plot_financial(y_roe, y_roe_pred, model_roe.resid, "ROE Model", "Actual ROE", "Predicted ROE")
    plot_financial(y_stock, y_stock_pred, model_stock.resid, "Stock Growth Model", "Actual Stock Growth", "Predicted Stock Growth")

def plot_regression_line(X, y_actual, y_pred, title, xlabel, ylabel):
    """Generates a scatter plot with regression line."""
    try:
        if 'overall_esg_score' not in X.columns:
            raise ValueError("Column 'overall_esg_score' not found in X.")
        
        X_esg = X['overall_esg_score']
        
        if len(X_esg) == 0 or len(y_actual) == 0 or len(y_pred) == 0:
            raise ValueError("Empty data detected. Ensure all inputs have values.")
        
        plt.figure(figsize=(8, 6))
        
        sns.scatterplot(x=X_esg, y=y_actual, color='blue', label='Actual')
        sns.lineplot(x=X_esg, y=y_pred, color='red', label='Regression Line')
        
        plt.title(f'{title} vs. ESG Score: Linear Regression', fontsize=14)
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.legend()
        plt.tight_layout()
        plt.show()
    except ValueError as ve:
        logging.warning(f"ValueError in plot_regression_line: {ve}")
        print(f"Warning: {ve}")
    except Exception as e:
        logging.error(f"Error in plot_regression_line: {e}")
        print("An error occurred while plotting the regression line.")


def build_and_plot_financial_model_with_regression(df):
    """Main function to extract variables, build models, predict, and plot regression lines."""
    try:
        # Extract variables
        X, y_roa, y_roe, y_stock = extract_variables(df)
        
        if X is None or y_roa is None or y_roe is None or y_stock is None:
            print("Insufficient data for model building.")
            return

        # Build the financial model
        model_roa, model_roe, model_stock = build_financial_model(X, y_roa, y_roe, y_stock)
        
        if model_roa is None or model_roe is None or model_stock is None:
            print("Model building failed.")
            return

        print("ROA-ESG Model Summary\n", model_roa.summary(), "\n", 
              "ROE-ESG Model Summary\n", model_roe.summary(), "\n", 
              "Stock Growth-ESG Model Summary\n", model_stock.summary())
        
        # Make predictions
        y_roa_pred, y_roe_pred, y_stock_pred = predict_values(model_roa, model_roe, model_stock, X)
        
        if y_roa_pred is None or y_roe_pred is None or y_stock_pred is None:
            print("Prediction failed.")
            return
        
        # Plot predicted vs actual and residuals
        plot_all_results(y_roa, y_roa_pred, model_roa, y_roe, y_roe_pred, model_roe, y_stock, y_stock_pred, model_stock)
        
        # Plot regression lines for ROA, ROE, and Stock Growth
        plot_regression_line(X, y_roa, y_roa_pred, "ROA", "ESG Score", "ROA")
        plot_regression_line(X, y_roe, y_roe_pred, "ROE", "ESG Score", "ROE")
        plot_regression_line(X, y_stock, y_stock_pred, "Stock", "ESG Score", "Stock Growth (%)")
        
    except Exception as e:
        print(f"Error in financial model pipeline: {e}")

def run():
    """Main function to execute the full pipeline."""
    supabase = connect_to_supabase()
    if supabase is None:
        print("Failed to connect to Supabase.")
        return
    
    esg_rag, stocks, roa_roe, esg_cat = fetch_data(supabase)
    if esg_rag is None or stocks is None or roa_roe is None or esg_cat is None:
        print("Failed to fetch data.")
        return
    
    format_data(esg_rag, stocks, roa_roe)
    stocks_return = transform_data(stocks)
    esg_rag, stocks_return, roa_roe = clean_data(esg_rag, stocks_return, roa_roe)
    esg_overall_score = compute_esg_scores(esg_rag, esg_cat)
    
    # Proceed with the RFE analysis
    df_features, features, targets = prep_rfe(esg_rag, roa_roe, stocks_return)
    if df_features is None or features is None or targets is None:
        print("Failed to prepare features for RFE.")
        return
    
    top_features_rfe, top_5_features = rfe(df_features, features, targets)
    
    df = merge_financial_esg_data(roa_roe, esg_overall_score, stocks_return)
    build_and_plot_financial_model_with_regression(df)
      
if __name__ == "__main__":
    run()