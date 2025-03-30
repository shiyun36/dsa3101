<div align="center">

# 🏆 DSA3101 Group 7 Project Instructions  

### 🌍 ESG Data Extraction & Analysis with NLP  

📌 Developed for **DSA3101** at the **National University of Singapore**  

</div>


## Table of Contents  

- [About the Project](#about-the-project)  
  - [ESG Data Extraction & Analysis with NLP](#esg-data-extraction--analysis-with-nlp)
  - [Tech Stack](#tech-stack)
  - [Pipeline](#pipeline)
  - [Database Schema](#database-schema)
- [Running The Project](#running-the-project)  
   - [Applications Needed](#applications-needed)  
   - [Dockerizing the Project](#dockerizing-the-project)  
   - [Running Python Scripts](#running-python-scripts)  
- [PowerBI Dashboard](#powerbi-dashboard)  
   - [Executive Summary](#executive-summary)  
   - [Company Summary](#company-summary)   
- [Group Members](#group-members)  
- [Acknowledgements](#acknowledgements)  



# About the Project
## ESG Data Extraction & Analysis with NLP
As ESG (Environmental, Social, and Governance) factors become central to corporate strategy and investor decisions, companies face increasing pressure to publish transparent and standardized ESG reports. However, the lack of consistency in reporting structures makes manual data extraction inefficient and error-prone.

This project leverages Natural Language Processing (NLP) and AI to automate ESG data extraction, normalization, and scoring. Our goal is to transform unstructured ESG reports into actionable insights, enabling businesses to benchmark performance, assess risks, and predict financial impact.

### Key Features:
1. Automated ESG Data Extraction – Structured data processing from unstructured reports

2. Metric Normalization – Standardizing ESG indicators for cross-industry comparison

3. ESG Scoring & Benchmarking – Aligning with industry standards to enhance transparency

By streamlining ESG analysis, we empower stakeholders with a data-driven impact dashboard to visualize trends and drive sustainability-focused decisions.

[🔼 Back to Top](#table-of-contents)

## Tech Stack
[![Power Bi](https://img.shields.io/badge/power_bi-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/products/docker-desktop/)
[![Hugging Face](https://img.shields.io/badge/hugging%20face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.io/)
[![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com/)

## Pipeline
![image](https://github.com/user-attachments/assets/266be462-0842-47dd-b664-866040f3353f)

## Database Schema
[![Supabase](https://img.shields.io/badge/Supabase-Database-green?logo=supabase&style=flat-square)](https://supabase.io/)
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


[🔼 Back to Top](#table-of-contents)

# Running The Project
## Applications Needed
Ensure that you have the following installed.
1. [![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/products/docker-desktop/)
2. [![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com/)
   
[🔼 Back to Top](#table-of-contents)

## Dockerizing the Project
1. Open a folder that you like and right click to open with Git-Bash or CMD. Clone the project with the following commands
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
   db_host=localhost
   db_password=password
   DATABASE_URL={CONTACT US}
   ```
   
   The directory should be:
   ```
   dsa3101/.env
   ```
5. To dockerize the application, run the commands below. The first line will take a while to run due to the big dependencies
  ```
  docker compose up -d
  ```

[🔼 Back to Top](#table-of-contents)

## Running Python Scripts
To use the python scripts in Docker, run the following

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

## Group Members

| Name           | GitHub         | Role |
|----------------|-----------------| ------ |
| Shi Yun    | [shiyun33](https://github.com/shiyun33)  | Group A |
| Jeremiah    | [jeremiah-tay](https://github.com/jeremiah-tay) | Group A |
| Tolentino Alexandra Morales   | [Shiraishie](https://github.com/Shiraishie) | Group A |
| Jing Zhi   | [jingzhing](https://github.com/jingzhing)  | Group A |
| Wei Jiang | [@github_username](https://github.com/github_username)  | Group A |
| Terence    | [@github_username](https://github.com/github_username)  | Group B |
| David Wong   | [davidwtk](https://github.com/davidwtk)  | Group B |
| Wynnona Pheeby   | [@github_username](https://github.com/github_username)  | Group B |
| Lim Song Ern, Shauna    | [shaunalim](https://github.com/shaunalim)  | Group B |
| Elise Lim Jia Jing   | [@github_username](https://github.com/github_username) | Group B |

[🔼 Back to Top](#table-of-contents)

## Acknowledgements
Many thanks to Professor Hernandez Marin Sergio and our TA Fauzan!

[🔼 Back to Top](#table-of-contents)


