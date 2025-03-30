# DSA3101 Group 7 Project Instructions

## About the Project
Environmental, Social and Governance (ESG) factors have become central to corporate strategy, investor decision-making and regulatory compliance. With the rising demand for transparency and accountability in sustainability, companies are increasingly required to publish detailed ESG reports. However, the manual extraction and analysis of ESG data remains labor-intensive and error-prone, particularly because these reports are often inconsistently structured. This results in a bottleneck for businesses trying to meet stakeholder demands. 
Our project thus aims to automate the extraction of ESG data using Natural Language Processing. By streamlining the extraction process, we aim to validate and interpret the data, transforming it into valuable insights. Our business goal is to provide an impact dashboard for stakeholders to visualize overall ESG trends and predict the financial impact of ESG performance on companies. This enables businesses to benchmark performance efficiently and deliver actionable insights.
The core challenge lies in the variation of ESG reporting formats. Companies use different frameworks, leading to non-standardized data that is difficult to compare across industries. This inefficiency hinders stakeholders’ ability to assess risks, identify trends, or make data-driven decisions. Moreover, the lack of standardization complicates cross-company comparisons.

By automating ESG analysis through NLP and AI, we aim to 
- Extract structured data, Normalize metrics.
- Generate scores aligned with industry benchmarks.

This approach not only enhances transparency but also helps companies align with global sustainability goals, mitigate risks, and unlock competitive advantages. Ultimately, our goal is to contribute to speeding up the building of a more sustainable and equitable global economy.

## Tech Stack
Containerizer
Docker

Frontend
PowerBI

Backend
HuggingFace Transformers

Database
SupaBase (PostGreSQL Online)


## Applications Needed
Ensure that you have the following installed.
1. Docker
2. Git

## Running and Dockerizing the Project
1. Open a folder that you like and right click to open with Git-Bash or CMD. Clone the project with the following commands
   ```
   git clone https://github.com/shiyun36/dsa3101.git
   ```
2. CD into the project directory with:
   ```
   cd dsa3101
   ```
3. Place the env file in this directory. Please contact us for the .env file.
   ```
   dsa3101/.env
   ```
4. To dockerize the application, run the commands below. The first line will take a while to run due to the big dependencies
  ```
  docker compose up -d
  ```
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

## Accesing PowerBI Dashboard


## Group Members
