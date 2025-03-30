# DSA3101 Group 7 Project Instructions Testing here 

## Table of Contents
- [About the Project](#about-the-project)
  - [ESG Data Extraction & Analysis with NLP](#esg-data-extraction--analysis-with-nlp)
  - [Tech Stack](#tech-stack)
- [Running The Project](#running-the-project)
   - [Applications Needed](#applications-needed)
   - [Dockerizing the Project](#dockerizing-the-project)
   - [Running Python Scripts](#running-python-scripts)
- [PowerBI Dashboard](#powerbi-dashboard)
   - [Executive Summary]
   - [Company Summary]
- [Details](#details)
- [Group Members](#group-members)
- [Acknowledgements](#acknowledgements)

# About the Project
## ESG Data Extraction & Analysis with NLP
As ESG (Environmental, Social, and Governance) factors become central to corporate strategy and investor decisions, companies face increasing pressure to publish transparent and standardized ESG reports. However, the lack of consistency in reporting structures makes manual data extraction inefficient and error-prone.

This project leverages Natural Language Processing (NLP) and AI to automate ESG data extraction, normalization, and scoring. Our goal is to transform unstructured ESG reports into actionable insights, enabling businesses to benchmark performance, assess risks, and predict financial impact.

Key Features:
1. Automated ESG Data Extraction – Structured data processing from unstructured reports

2. Metric Normalization – Standardizing ESG indicators for cross-industry comparison

3. ESG Scoring & Benchmarking – Aligning with industry standards to enhance transparency

By streamlining ESG analysis, we empower stakeholders with a data-driven impact dashboard to visualize trends and drive sustainability-focused decisions.

[🔼 Back to Top](#table-of-contents)

## Tech Stack
[![Docker](https://img.shields.io/badge/Docker-Container-blue?logo=docker&style=flat-square)](https://www.docker.com/products/docker-desktop/)
[![PowerBI](https://img.shields.io/badge/PowerBI-Frontend-orange?logo=powerbi&style=flat-square)](https://powerbi.microsoft.com/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Backend-blue?logo=huggingface&style=flat-square)](https://huggingface.co/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-green?logo=supabase&style=flat-square)](https://supabase.io/)
[![Git](https://img.shields.io/badge/Git-Version%20Control-F05032?logo=git&style=flat-square)](https://git-scm.com/)

[🔼 Back to Top](#table-of-contents)

# Running The Project
## Applications Needed
Ensure that you have the following installed.
1. [![Docker](https://img.shields.io/badge/Docker-Container-blue?logo=docker&style=flat-square)](https://www.docker.com/products/docker-desktop/)
2. [![Git](https://img.shields.io/badge/Git-Version%20Control-F05032?logo=git&style=flat-square)](https://git-scm.com/)
   
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

| Name           | Email          |
|----------------|-----------------|
| Terence    | e0726538@u.nus.edu  |
| David Wong   | e0958026@u.nus.edu  |
| Wynnona Pheeby   | e0985898@u.nus.edu  |
| Shi Yun    | e0773037@u.nus.edu  |
| Jeremiah    | e0726076@u.nus.edu  |
| Lim Song Ern, Shauna    | e0968215@u.nus.edu  |
| Tolentino Alexandra Morales    | e0969604@u.nus.edu  |
| Elise Lim Jia Jing   | e0970449@u.nus.edu  |
| Jing Zhi   | e0726423@u.nus.edu  |
| Wei Jiang | e0775132@u.nus.edu  |

[🔼 Back to Top](#table-of-contents)

## Acknowledgements

[🔼 Back to Top](#table-of-contents)


