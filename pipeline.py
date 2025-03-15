from scripts.ask_llm import ask_llm
from scripts.pdf_table_extract import extract_tables
from scripts.prompts import prompts
from scripts.json_clean import json_clean
from dotenv import load_dotenv
import os
from openai import OpenAI
from db.scripts.db_esg_bert import db_esg_bert
from db.scripts.db_esg_llm import db_esg_llm
from db.scripts.db_esg_executive import db_esg_table
from scripts.pdf_to_text_reader_script import convert_ocr_pdf_to_text
from transformers import pipeline
import pandas as pd
import json
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
import datetime
from scripts.get_financial_data import get_financial_data

#OCR Script run here and output pdf_file
####################
## Insert Here ##
####################

################# PDF To Json ############
#Change pdf_file eventually to the pdf we need
pdf_file = '/home/shiro/dsa3101/Datasets/ocr_esg/Tech/Na/DataDog_2024_ocr.pdf'
doc_json = convert_ocr_pdf_to_text(pdf_file)
###################################################

############### BERT #######################
##Bert Model Run here ##Placeholder BERT Model
pipe = pipeline("text-classification", model="nbroad/ESG-BERT")
res = pipe(doc_json,truncation=True)
#################

############################## DUMMY DATA GENERATION ###################
## Dummy output as im using placeholder bert-model ##Can ignore this after
esg_categories = {
    "Business_Ethics": "Governance",
    "Management_Of_Legal_And_Regulatory_Framework": "Governance",
    "Business_Model_Resilience": "Governance",
    "Human_Rights_And_Community_Relations": "Social",
    "Access_And_Affordability": "Social",
    "Employee_Health_And_Safety": "Social",
    "Employee_Engagement_Inclusion_And_Diversity": "Social",
    "Critical_Incident_Risk_Management": "Social",
    "Product_Quality_And_Safety": "Social",
    "Supply_Chain_Management": "Social",
    "Labor_Practices": "Social",
    "Customer_Privacy": "Social",
    "Selling_Practices_And_Product_Labeling": "Social",
    "GHG_Emissions": "Environmental",
    "Physical_Impacts_Of_Climate_Change": "Environmental",
    "Energy_Management": "Environmental",
    "Waste_And_Hazardous_Materials_Management": "Environmental",
    "Water_And_Wastewater_Management": "Environmental",
    "Ecological_Impacts": "Environmental",
    "Air_Quality": "Environmental",
    "Director_Removal": "Governance",
    "Systemic_Risk_Management": "Governance",
    "Product_Design_And_Lifecycle_Management": "Governance",
    "Competitive_Behavior": "Governance"
}

res_labels = pd.DataFrame(res)
res_labels['cat'] = res_labels['label'].map(esg_categories)
res_labels['label'] = res_labels['cat'] + ' - ' + res_labels['label']
res_dummy =res_labels[['label','score']].to_json(orient='records')
res_dummy = json.loads(res_dummy)
#################### Dummy label in the format of {'label': 'ESG_Cat - ESG_subcat', 'score'}

################# LLM Model and further data extraction ###################
## Add label and scores to the list of sentences extracted
df = pd.DataFrame(doc_json, columns=['sentence'])
df[['label','score']] = pd.DataFrame(res_dummy) ##dummy res data

#Split the ESG_Cat and ESG_subcat to seperate columns
df['label'][0].split(' - ')
df[['esg_cat','esg_subcat']] = df['label'].str.split(' - ',expand=True)
df = df [['sentence','esg_cat','esg_subcat','score']]

## Score filtering
df_score_filtered = df[df['score'] > 0.8]

## Tabular Data Extraction
tabular = extract_tables('/home/shiro/dsa3101/Datasets/ocr_esg/Health/NA/Pfizer_2022_ocr.pdf')

## LLM_Data DF without scores
data = df_score_filtered[['sentence','esg_cat','esg_subcat']]

## LLM Output , it loops through E,S,G categories and runs LLM model three times to lessen hallucination
output = ask_llm(data['esg_cat'].unique(),data, tabular, prompts)

## Clean LLM Output as it has ```json``` etc
cleaned_output = [json.loads(i) for i in json_clean(output)]  

## Extract company meta_data
company = cleaned_output[0][0]['company'] #take one entry and extract company,year,ticker to combine to esg_bert
company_year = cleaned_output[0][0]['year']
company_ticker = cleaned_output[0][0]['ticker']

## Uses original data_frame that is unfiltered (So we can let analyst filter the data on their own and change labels to refeed into model and incase want frontend)
## 
df[['company','year','ticker']] = [company,company_year,company_ticker] 
print(company)

########### DB Insertion ##########
db_esg_table(tabular, company,company_year,company_ticker)
db_esg_bert(df)
db_esg_llm(cleaned_output)

###### Yahoo Finance Data DB #####
get_financial_data(company_ticker, company)

# print('Table Datas', tabular)
# print('Company', company)
# print('company_year Datas', company_year)
# print('company_ticker Datas', company_ticker)
# print('cleaned_output', cleaned_output)
