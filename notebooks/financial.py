import pandas as pd
import yahooquery as yq
import yfinance as yf
from dotenv import load_dotenv
import psycopg2
from db.scripts.db_insert_stocks import insert_stocks
from db.scripts.db_insert_roa_roe import insert_roa_roe
from db.scripts.get_ticker_symbol import get_ticker_symbol
from db.scripts.get_roa_roe import get_roa_roe
from db.scripts.get_stocks import get_stocks
import os

def financial():
    ## Getting the company tickers dataframe
    try:
        load_dotenv('.env')
        ## Local DB ##
        # db_name = os.getenv('db_name')
        # db_user = os.getenv('db_user')
        # db_port = os.getenv('db_port')
        # db_host = os.getenv('db_host')
        # db_password = os.getenv('db_password')
        # conn = psycopg2.connect(f"dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}")

        ## Supabase ##
        db_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(db_url)

        cur = conn.cursor()
        cur.execute('SELECT * FROM company_ticker')
        data = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        df = pd.DataFrame(data, columns=columns)
        print(df)

        ## getting the company list from our esg_rags
        cur.execute('SELECT DISTINCT company from esg_text_table')
        res = list(cur.fetchall())
        result_list = [row[0] for row in res] ## Names of the companies
        print(result_list)
        ## getting ticker_symbols
        symbols = []
        for i in result_list:
            symbols.append(get_ticker_symbol(i,df))
        print(symbols)

        ## getting ticker_symbols for non private companies
        company_ticker = pd.DataFrame({'symbol': symbols, 'name': result_list})
        company_ticker = company_ticker[company_ticker['symbol'].notna()]

        ## Scrapping past 10 years of stock prices if it exist and inserting into DB
        for index,row in company_ticker.iterrows():
            ticker = row['symbol']
            company = row['name']
            stocks = get_stocks(ticker,company) #returns df
            if stocks is None:
                continue
            insert_stocks(stocks)

        ## Getting past ROA/ROE data, only 4 years available and inserting into the db
        for index,row in company_ticker.iterrows():
            ticker = row['symbol']
            company = row['name']
            roa_roe = get_roa_roe(ticker,company)
            if roa_roe is None:
                continue
            insert_roa_roe(roa_roe)
        cur.close()
        conn.close()
    except Exception as e:
        print('Error getting financial data', e)