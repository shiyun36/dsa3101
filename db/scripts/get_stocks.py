import yfinance as yf
import pandas as pd

def get_stocks(ticker,company_name):
    stock = yf.Ticker(ticker)
    monthly_stock = stock.history(period="10y", interval="1mo")["Close"] #check if empty
    if monthly_stock.empty == True:
        return None
    stocks = pd.DataFrame(monthly_stock.reset_index(), columns=['Date','Close']) ##df with stock
    stocks['company'] = company_name
    return stocks
    