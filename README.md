<div align="center">

# 🏆 DSA3101 Group 7 Project Instructions 🏆

### 🌍 ESG Data Extraction & Analysis with NLP 🌍
![ESG1-ezgif com-loop-count (1)](https://github.com/user-attachments/assets/d9a30c62-cf78-477b-8bce-8b3b931bfd7f)

### 📌 Developed for **DSA3101** at the **National University of Singapore** 📌

</div>


## Table of Contents  

- [About the Project](#about-the-project)  
  - [ESG Data Extraction & Analysis with NLP](#esg-data-extraction--analysis-with-nlp)
  - [Features](#features)
  - [Tech Stack](#tech-stack)
  - [Pipeline](#pipeline)
  - [Repository Structure](#repository-structure)
  - [Database Schema](#database-schema)
- [Running The Project](#running-the-project)  
   - [Applications Needed](#applications-needed)  
   - [Dockerizing the Project](#dockerizing-the-project)  
   - [Running Python Scripts](#running-python-scripts)  
- [PowerBI Dashboard](#powerbi-dashboard)  
   - [Executive Summary](#executive-summary)  
   - [Company Summary](#company-summary)
- [Local Development](#local-development)
- [Group Members](#group-members)  
- [Acknowledgements](#acknowledgements)  



# About the Project
## ESG Data Extraction & Analysis with NLP
As ESG (Environmental, Social, and Governance) factors become central to corporate strategy and investor decisions, companies face increasing pressure to publish transparent and standardized ESG reports. However, the lack of consistency in reporting structures makes manual data extraction inefficient and error-prone.

This project leverages Natural Language Processing (NLP) and AI to automate ESG data extraction, normalization, and scoring. Our goal is to transform unstructured ESG reports into actionable insights, enabling businesses to benchmark performance, assess risks, and predict financial impact.

## Features:
### 1. Automated ESG Data Extraction – Structured data processing from unstructured reports

### 2. Metric Normalization using RAG – Standardizing ESG indicators for cross-industry comparison
We use Retrieval Augmented Generation (RAG) where the LLM is connected to our ESG database and retrieves the data for each ESG metric and normalizes it based on industry averages.
We do this using a JSON-based query system. For each ESG metric, we send 2 queries: value_query, which extracts the data for the metric and scoring_query, which normalizes the data to between 0 and 1.

### 3. ESG Scoring & Summary Dashboards - Benchmarking and visualisation of ESG data of companies
Our scoring system rates the ESG performance of each company out of 10, where a higher score indicates better performance.

### 4. Prediction Model for Financial Impact of ESG performance - Determine key ESG factors affecting financial performance
Our prediction model benchmarks companies using overall ESG scores, analyzing their relationship with financial metrics such as ROA, ROE, and stock growth. Separately, to identify the most influential ESG factors, we applied Recursive Feature Elimination (RFE), selecting the top five ESG metrics that best predict financial performance.

Due to limited standardized ESG data, we initially fitted a simple linear regression model to estimate the financial impact of ESG scores across companies. However, as more data becomes available, the model can and should be refined to assess company-specific ESG-financial relationships. Future iterations may incorporate time-lagged financials, individual ESG metrics, and advanced models like ARIMA or VARMAX for deeper, more accurate insights.

## Tech Stack
[![Power Bi](https://img.shields.io/badge/power_bi-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/products/docker-desktop/)
[![Hugging Face](https://img.shields.io/badge/hugging%20face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/)
![ChatGPT](https://img.shields.io/badge/chatGPT-74aa9c?style=for-the-badge&logo=openai&logoColor=white)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.io/)
[![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com/)

## Pipeline
![image](https://github.com/user-attachments/assets/7b926fad-8614-457a-8727-0a21e386e883)


[🔼 Back to Top](#table-of-contents)

## Repository Structure
```
add our file structures here :D
```

[🔼 Back to Top](#table-of-contents)

## Database Schema
Our Database is hosted online @ [![Supabase](https://img.shields.io/badge/Supabase-Database-green?logo=supabase&style=flat-square)](https://supabase.io/). For access, please contact us with your email to be added into the organization.

We have also included PostGreSQL database that is unpopulated with pgAdmin4 interface for local development. You can find the details at [Local Development](#local-development).

### `esg_text_table`
Stores ESG report text for each company, year, country, and industry.

| Column     | Type     | Description                               |
|------------|----------|-------------------------------------------|
| `company`  | VARCHAR  | Name of the company                       |
| `year`     | INT      | Year of the ESG report                    |
| `country`  | VARCHAR  | Country where the company is located     |
| `industry` | VARCHAR  | Industry the company belongs to           |
| `esg_text` | VARCHAR     | ESG Report Sentence                      |

### `esg_rag_table`
Stores extracted ESG values and final scores for companies based on different topics in ESG.

| Column         | Type   | Description                                |
|----------------|--------|--------------------------------------------|
| `company`      | VARCHAR| Name of the company                        |
| `industry`     | VARCHAR| Industry of the company                    |
| `country`      | VARCHAR| Country where the company is based        |
| `year`         | INT    | Year of the ESG assessment                 |
| `topic`        | TEXT   | Topic of the ESG assessment (e.g., environment, governance) |
| `extracted_values` | TEXT | Values extracted for the topic            |
| `final_score`  | FLOAT  | Final ESG score                            |
```sql
CONSTRAINT esg_rag_pk PRIMARY KEY (company, industry, country, year,topic)
CONSTRAINT unique_esg_rag_entry UNIQUE (company,industry,country,year, topic,extracted_values,final_score)
```
### `stocks_table`
Stores stock price data for companies scraped from Yahoo Finance.

| Column  | Type     | Description                               |
|---------|----------|-------------------------------------------|
| `company`| VARCHAR | Name of the company                       |
| `date`   | DATE     | Date of the stock price                   |
| `close`  | FLOAT    | Closing stock price                       |
```sql
CONSTRAINT unique_stock_entry UNIQUE (company, date)
```

### `roa_roe_table`
Stores financial metrics: Return on Assets (ROA) and Return on Equity (ROE) for companies scraped from Yahoo Finance.

| Column  | Type     | Description                               |
|---------|----------|-------------------------------------------|
| `company`| VARCHAR | Name of the company                       |
| `date`   | DATE     | Date of the financial metrics             |
| `roa`    | FLOAT    | Return on Assets                         |
| `roe`    | FLOAT    | Return on Equity                         |
```sql
CONSTRAINT unique_roa_roe_entry UNIQUE (company, date)
```
### `region_table`
Maps countries to their respective regions and subregions.

| Column    | Type     | Description                               |
|-----------|----------|-------------------------------------------|
| `country` | VARCHAR  | Country name                             |
| `region`  | VARCHAR  | Geographical region                      |
| `subregion`| VARCHAR | Subregion of the country                  |
```sql
CONSTRAINT unique_region_entry UNIQUE (country, region, subregion)
```
### `company_ticker`
Maps company names to their stock ticker symbols. Else the api will search yahoo finance.

| Column       | Type   | Description                              |
|--------------|--------|------------------------------------------|
| `symbol`     | TEXT   | Stock ticker symbol                      |
| `company_name` | TEXT | Name of the company                      |

### `esg_financial_model_table`
Gives the top 5 features used to predict financial impact from ESG scores.

| Column       | Type   | Description                              |
|--------------|--------|------------------------------------------|
| `variable`     | VARCHAR   | The variable the feature belongs like roa, roe, stock growth, overall                      |
| `feature` | VARCHAR | Features that affect the variable like Current Employees by Gender                     |
| `rank` | INT | Rank of the feature                     |

### `esg_financial_model_top_features_table`
Output of our predictive model.

| Column       | Type   | Description                              |
|--------------|--------|------------------------------------------|
| `esg_score`     | FLOAT   | Given esg_score input                      |
| `roa_actual` | FLOAT | Actual roa                    |
| `roa_predicted`     | FLOAT   | Model predicted roa                     |
| `roe_actual`     | FLOAT   | Actual roe                       |
| `roe_predicted` | FLOAT | Model predicted roe                     |
| `stock_growth_actual`     | FLOAT   | Actual stock growth                     |
| `stock_growth_predicted` | FLOAT | Model predicted roa stock growth                   |


[🔼 Back to Top](#table-of-contents)

# Running The Project
## Applications Needed
Ensure that you have the following installed and specs.
1. [![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/products/docker-desktop/)
2. [![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com/)
3. ```‼️Atleast 20GB of Storage ‼️```
4. ```‼️‼️‼️ NOT CONNECTED TO NUS WIFI AS IT BLOCKS CONNECTIONS```


## Dockerizing the Project
1. Open a folder that you like and right click to open with Git-Bash or CMD/PowerShell. Clone the project with the following commands
   ```
   git clone https://github.com/shiyun36/dsa3101.git
   ```
2. CD into the project directory with:
   ```
   cd dsa3101
   ```
3. Place the env file in this directory. Please contact us for the .env file. But the env file will look like:
   ```
   db_name=postgres
   db_user=postgres
   db_port=5432
   db_host=postgres
   db_password=password
   DATABASE_URL={CONTACT US}
   SUPABASE_URL={CONTACT US}
   SUPABASE_KEY={CONTACT US}
   ```
   
   The directory should be:
   ```
   dsa3101/.env
   ```
5. To dockerize the application, run the commands below. This will take a while to run due to the dependencies.
  ```
  docker compose up -d
  ```
> ⚠️ **Important:** This can take awhile to load depending on your computer specs.
> 
[🔼 Back to Top](#table-of-contents)

## Running Python Scripts
To use the python scripts in Docker, run the following in the same terminal after the above.

1. Run this command once
```
docker-compose exec app bash
```

2. Run with the directory of script
```
python {script to run add file directory here}
```

[🔼 Back to Top](#table-of-contents)

## PowerBI Dashboard
### Executive Summary
### Company Summary

[🔼 Back to Top](#table-of-contents)

## Local Development
If the need for local development arises with a locally hosted database, follow the instructions below. Ensure that the Docker Container has started.
1. Before Dockerizing the container, go to the db folders and its scripts and the main script. Uncomment the lines with
   ```
     db_name = os.getenv('db_name')
     db_user = os.getenv('db_user')
     db_port = os.getenv('db_port')
     db_host = os.getenv('db_host')
     db_password = os.getenv('db_password')
     conn = psycopg2.connect(f"dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}")
   ```
  and Comment out line with `## SupaBase DB ##`.
  
  If missing in main file, add the above and comment out the DATABASE_URL and conn with DATABASE_URL.
  
  Then run step 5 from [Dockerizing the Project](#dockerizing-the-project)
  
2. Run the commands to create the local database in PostGreSQL.
```
docker-compose exec app bash
python ./db/db.py
```
3. Follow instructions from [Running Python Scripts](#running-python-scripts).
4.  To access the local DB with the pgAdmin4 interface. Ensure that pgAdmin4 container has started and put the below in your browser.
```
localhost:80
```
Sign in with
```
user@email.com
password
```
> ⚠️ **Important:** This can take awhile before localhost is accesible due to container size.
5. Click on Add New Server and input the following and save:
```
General Tab:
  Name: postgres (or anything you want)
Connection Tab:
  Host name/address: postgres
  port: 5432
  username: postgres
  Password: password
```
6. You can now access the postgres DB and the tables. Use SQL to query or right click tables to view data.

[🔼 Back to Top](#table-of-contents)

## Group Members

| Name           | GitHub         | Role |
|----------------|-----------------| ------ |
| Shi Yun    | [shiyun33](https://github.com/shiyun33)  | Group A |
| Jeremiah    | [jeremiah-tay](https://github.com/jeremiah-tay) | Group A |
| Tolentino Alexandra Morales   | [Shiraishie](https://github.com/Shiraishie) | Group A |
| Jing Zhi   | [jingzhing](https://github.com/jingzhing)  | Group A |
| Wei Jiang | [Bearbeargood](https://github.com/Bearbeargood)  | Group A |
| Terence    | [terencelai31](https://github.com/terencelai31)  | Group B |
| David Wong   | [davidwtk](https://github.com/davidwtk)  | Group B |
| Wynnona Pheeby   | [wynpyy](https://github.com/wynpyy)  | Group B |
| Lim Song Ern, Shauna    | [shaunalim](https://github.com/shaunalim)  | Group B |
| Elise Lim Jia Jing   | [mile-sile](https://github.com/mile-sile) | Group B |

[🔼 Back to Top](#table-of-contents)

## Acknowledgements
Many thanks to Professor Hernandez Marin Sergio and our TA Fauzan!

[🔼 Back to Top](#table-of-contents)


