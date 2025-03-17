import yfinance as yf

def get_roa_roe(ticker,company_name):
    stock = yf.Ticker(ticker)
    income_statements = stock.income_stmt
    balance_sheets = stock.balance_sheet
    if income_statements.empty == True or balance_sheets.empty == True:
        return None
    df = (income_statements.T['Net Income'] / balance_sheets.T["Total Assets"]).reset_index().rename(columns={'index': 'Date', 0: 'roa'})
    roe = (income_statements.T['Net Income'] /balance_sheets.T['Stockholders Equity']).reset_index().rename(columns={'index': 'Date', 0: 'roe'})
    df['roe']  = roe['roe']
    df['company'] = company_name
    return df