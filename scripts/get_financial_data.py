import psycopg2
from dotenv import load_dotenv
import os
import json
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
import datetime

def get_financial_data(ticker,company):
    load_dotenv()

    db_name = os.getenv('db_name')
    db_user = os.getenv('db_user')
    db_port = os.getenv('db_port')
    db_host = os.getenv('db_host')
    db_password = os.getenv('db_password')

    # #create cursor & conn
    # conn = psycopg2.connect(f"dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}")
    # cur = conn.cursor()
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}') #Or change to supabase

    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        sustainability = stock.sustainability
        income_stmt = stock.financials  # Income Statement
        balance_sheet = stock.balance_sheet  # Balance Sh
        cash_flow = stock.cash_flow

        ### Sustainability ####
        esg_scores = sustainability['esgScores']
        flattened_data = {
        'company': company,
        'maxAge': esg_scores['maxAge'],
        'totalEsg': esg_scores['totalEsg'],
        'environmentScore': esg_scores['environmentScore'],
        'socialScore': esg_scores['socialScore'],
        'governanceScore': esg_scores['governanceScore'],
        'ratingYear': esg_scores['ratingYear'],
        'ratingMonth': esg_scores['ratingMonth'],
        'highestControversy': esg_scores['highestControversy'],
        'peerCount': esg_scores['peerCount'],
        'esgPerformance': esg_scores['esgPerformance'],
        'peerGroup': esg_scores['peerGroup'],
        'relatedControversy': esg_scores['relatedControversy'],
        'peerEsgScorePerformance_min': esg_scores['peerEsgScorePerformance']['min'],
        'peerEsgScorePerformance_avg': esg_scores['peerEsgScorePerformance']['avg'],
        'peerEsgScorePerformance_max': esg_scores['peerEsgScorePerformance']['max'],
        'peerGovernancePerformance_min': esg_scores['peerGovernancePerformance']['min'],
        'peerGovernancePerformance_avg': esg_scores['peerGovernancePerformance']['avg'],
        'peerGovernancePerformance_max': esg_scores['peerGovernancePerformance']['max'],
        'peerSocialPerformance_min': esg_scores['peerSocialPerformance']['min'],
        'peerSocialPerformance_avg': esg_scores['peerSocialPerformance']['avg'],
        'peerSocialPerformance_max': esg_scores['peerSocialPerformance']['max'],
        'peerEnvironmentPerformance_min': esg_scores['peerEnvironmentPerformance']['min'],
        'peerEnvironmentPerformance_avg': esg_scores['peerEnvironmentPerformance']['avg'],
        'peerEnvironmentPerformance_max': esg_scores['peerEnvironmentPerformance']['max'],
        'peerHighestControversyPerformance_min': esg_scores['peerHighestControversyPerformance']['min'],
        'peerHighestControversyPerformance_avg': esg_scores['peerHighestControversyPerformance']['avg'],
        'peerHighestControversyPerformance_max': esg_scores['peerHighestControversyPerformance']['max'],
        'percentile': esg_scores['percentile'],
        'environmentPercentile': esg_scores['environmentPercentile'],
        'socialPercentile': esg_scores['socialPercentile'],
        'governancePercentile': esg_scores['governancePercentile'],
        'adult': esg_scores['adult'],
        'alcoholic': esg_scores['alcoholic'],
        'animalTesting': esg_scores['animalTesting'],
        'catholic': esg_scores['catholic'],
        'controversialWeapons': esg_scores['controversialWeapons'],
        'smallArms': esg_scores['smallArms'],
        'furLeather': esg_scores['furLeather'],
        'gambling': esg_scores['gambling'],
        'gmo': esg_scores['gmo'],
        'militaryContract': esg_scores['militaryContract'],
        'nuclear': esg_scores['nuclear'],
        'pesticides': esg_scores['pesticides'],
        'palmOil': esg_scores['palmOil'],
        'coal': esg_scores['coal'],
        'tobacco': esg_scores['tobacco']
        }

        pd.DataFrame(flattened_data).to_sql('esg_yahoo_sustainability', engine, index=False, if_exists='append')

        ### Income Statement ###
        index_income = income_stmt.T.index
        income_t = income_stmt.T
        income_t['date'] = index_income
        income_t.reset_index(drop=True, inplace=True)
        income_t['company'] = company
        income_t.to_sql('esg_yahoo_income', engine, if_exists='append')

        ### Balance Sheet ### 
        index_bal = balance_sheet.T.index
        bal_t = balance_sheet.T
        bal_t['date'] = index_bal
        bal_t.reset_index(drop=True, inplace=True)
        bal_t['company'] = company
        bal_t.to_sql('esg_yahoo_balance', engine, if_exists='append')
        ### Cash Flow ###
        index_cash = balance_sheet.T.index
        cash_flow = cash_flow.T
        cash_flow['date'] = index_cash
        cash_flow.reset_index(drop=True, inplace=True)
        cash_flow['company'] = company
        cash_flow.to_sql('esg_yahoo_cashflow', engine, if_exists='append')

        ### stock info ##
        financial_data = {
            'company': company,
            'year': datetime.datetime.utcfromtimestamp(info.get('mostRecentQuarter')).strftime('%Y'),
            'ROA': info.get('returnOnAssets'),
            'ROE': info.get('returnOnEquity'),
            'netIncomeToCommon': info.get('netIncomeToCommon'),
            'trailingPE': info.get('trailingPE'),
            'forwardPE': info.get('forwardPE'),
            'grossProfits': info.get('grossProfits'),
            'operatingCashflow': info.get('operatingCashflow'),
            'freeCashflow': info.get('freeCashflow'),
            'totalRevenue': info.get('totalRevenue'),
            'bookValue': info.get('bookValue'),
            'payoutRatio': info.get('payoutRatio'),
            'grossMargins': info.get('grossMargins'),
            'ebitdaMargins': info.get('ebitdaMargins'),
            'marketCap': info.get('marketCap'),
            'priceToBook': info.get('priceToBook'),
            'enterpriseValue': info.get('enterpriseValue'),
            'dividendRate': info.get('dividendRate'),
            'dividendYield': info.get('dividendYield'),
            'fiveYearAvgDividendYield': info.get('fiveYearAvgDividendYield'),
            'debtToEquity': info.get('debtToEquity'),
            'quickRatio': info.get('quickRatio'),
            'currentRatio': info.get('currentRatio'),
            'auditRisk': info.get('auditRisk'),
            'boardRisk': info.get('boardRisk'),
            'compensationRisk': info.get('compensationRisk'),
            'shareHolderRightsRisk': info.get('shareHolderRightsRisk')
        }
        print(financial_data)
        pd.DataFrame([financial_data]).to_sql('esg_stock', engine, index=False, if_exists='append')
    
    except Exception as e:
        print('No available data')