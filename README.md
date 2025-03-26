# DSA3101 Project Wiki
## Project Overview 
Environmental, Social and Governance (ESG) factors have become central to corporate strategy, investor decision-making and regulatory compliance. With the rising demand for transparency and accountability in sustainability, companies are increasingly required to publish detailed ESG reports. However, the manual extraction and analysis of ESG data remains labor-intensive and error-prone, particularly because these reports are often inconsistently structured. This results in a bottleneck for businesses trying to meet stakeholder demands. 
Our project thus aims to automate the extraction of ESG data using Natural Language Processing. By streamlining the extraction process, we aim to validate and interpret the data, transforming it into valuable insights. Our business goal is to provide an impact dashboard for stakeholders to visualize overall ESG trends and predict the financial impact of ESG performance on companies. This enables businesses to benchmark performance efficiently and deliver actionable insights.
The core challenge lies in the variation of ESG reporting formats. Companies use different frameworks, leading to non-standardized data that is difficult to compare across industries. This inefficiency hinders stakeholders’ ability to assess risks, identify trends, or make data-driven decisions. Moreover, the lack of standardization complicates cross-company comparisons.
By automating ESG analysis through NLP and AI, we aim to extract structured data, normalize metrics, and generate scores aligned with industry benchmarks. This approach not only enhances transparency but also helps companies align with global sustainability goals, mitigate risks, and unlock competitive advantages. Ultimately, our goal is to contribute to speeding up the building of a more sustainable and equitable global economy.


## Key Questions
### 1. How can we develop an effective NLP algorithm to extract ESG information from unstructured reports?
Methodology:
Download ESG reports of companies of varying size and geographical locations to diversify data sources
Used OCR Scraper to extract images from PDF reports
Trained and fine-tuned a classification model to classify the text chunks saved into individual E,S,G categories. Extracted them using NER and scored them based on evaluation frameworks. However, we realised this was not feasible.
Used RAG to extract metrics and values from the categorized texts as context for LLM to compute the score for each ESG metric. 


### 2. How can we ensure the accuracy and reliability of the extracted ESG information?
To ensure the accuracy of extracted ESG data, we perform hallucination checks to mitigate common LLM errors. To enhance reliability, we use a Human-In-The-Loop (HITL) system, combining AI's efficiency with human oversight to address varying ESG reporting styles across industries and regions.
In this system, AI extracts data and generates scores based on predefined models, which are then reviewed by analysts to correct errors and refine outputs. Key features include:
User Interface: Intuitive front-end for efficient review of AI-generated ESG insights.
Confidence Scores: Highlights low-confidence data to focus analyst attention.
Continuous Feedback: Analyst corrections are fed back into the model for ongoing improvement.
This hybrid approach ensures accurate ESG reporting, enhancing stakeholder trust in our algorithm.


### 3. How can we adapt the algorithm to changing ESG reporting standards?
Transfer learning allows pre-trained models to leverage existing ESG standards knowledge, while being fine-tuned to adapt to new industries and reporting styles with minimal retraining. This ensures the model remains effective across various regulatory frameworks.
Human-in-the-loop (HITL) corrections and automated retraining further refine the model, while adaptive learning mechanisms enable dynamic adjustments to shifts in ESG reporting trends, such as new carbon emissions regulations. To maintain relevance, organizations must establish a pipeline to monitor regulatory changes and best practices.
This enables businesses, investors, and regulators to access up-to-date, accurate ESG insights, ensuring compliance with evolving standards.


### 4. What are the potential limitations of NLP in extracting ESG data, and how can we address them? 
One major issue is the lack of contextual understanding—basic methods like keyword matching can misinterpret future goals as current achievements. Advanced transformer-based models, such as ChatGPT, better maintain context and understand complex language.
Another challenge is NLP's difficulty in answering specific ESG questions, such as extracting Scope 3 emissions targets. Large Language Models (LLMs) with question-answering capabilities, combined with retrieval-augmented generation (RAG), improve accuracy by providing more relevant information from source documents.
Initially, we created a generalized JSON for RAG retrieval, incorporating queries for each metric. However, this approach proved too broad and ineffective. As a result, we developed specific JSONs tailored to individual sub-industries to get better outputs. While this improved RAG retrieval, we recognized that this method is not scalable. A more sustainable solution requires fine-tuning generalized queries or using external data for broader validation.


### 5. How can we ensure the scalability of the ESG data extraction system to handle large volumes of reports from multiple industries? 
To handle large volumes of ESG data extraction efficiently, we can use cloud-based and distributed computing.
Cloud Storage: ESG Reports can be stored in AWS S3 which is scalable rather than local machines with storage limits.
Batch Processing with Apache Spark: Every week, Spark processes data in parallel across multiple worker nodes with distributed computing, making it faster and fault-tolerant.
Real-Time Processing with Apache Kafka: Kafka can stream-process ESG data as soon as new reports are available if live data is required.
Local Parallel Processing: For smaller tasks like this project, we can still use multiple CPU cores for batch-processing, though it’s limited by the available hardware.
This approach ensures speed, scalability, and reliability for ESG data extraction.


### 6. How can we evaluate ESG performance using the structured data obtained from the algorithm? 
SGX ESG Framework:
- Total Metrics: 23
- Environment: 4 metrics
- Social: 11 metrics
- Governance: 8 metrics

Standardization:
- Metrics standardized to a score between 0 and 1
- Scoring based on data type and industry benchmarks

Weightage:
- Equal weightage (33%) applied to each ESG category
- Final ESG Score: Derived out of 10

Key Insights:
- Standardized ESG score provides a clear, quantifiable measure of a company’s ESG performance
- Facilitates easy comparison across industries

Business Impact & Actionable Recommendations: 
Companies can integrate ESG performance into KPIs, track progress, and identify areas for improvement. To improve, businesses should:
1. Leverage ESG Scores:
    - Benchmark against industry peers  
    - Set measurable sustainability goals

2. Improve Reporting Transparency:
    - Enhance data collection for accurate, meaningful ESG scores


### 7. What are key trends in ESG performance within the selected industry?
We analysed the ESG performance of companies in the financial and healthcare industries within Singapore. 

Financial Industry (Banks):
- ESG score: ~7/10
- Governance: Strong (3.05/3.33) – Excellent corporate governance and board diversity
- Environmental: Poor (1.86/3.33) – Conservative approach to reducing emissions

Healthcare Industry (Private Companies):
- ESG score: ~6.4/10
- Governance:  Strong (2.5/3.33)
- Social: Poor (1.71/3.33) – High turnover rates, disproportionate employee gender ratios

Overall Findings:
- Strong governance across both sectors
- Significant improvements needed in environmental and social ESG factors


### 8. How can we present ESG performance insights in a clear and actionable way? 
We propose a two-section dashboard:
1. Executive Summary: A high-level glance of ESG scores and metrics, allowing users to filter the year or region.
2. Company-Specific Details: A deep dive into the analysis of an individual company’s performance over time.

The dashboard includes:
- Clear Navigation: Tabs for industry, country, and trend analysis.
- Interactive Filters: Let users select industries, regions, and ESG factors.
- Color Coding: Green/red for strong/weak ESG performance.

Visualization methods used include:
- Heatmaps and Ranking Tables: Highlight top and bottom performers.
- Time-Series Line Charts: Track ESG trends.
- Benchmark Comparisons: Contextualize peer performance.
- Regression Plots: Link ESG scores to financial metrics.
This approach ensures the dashboard meets the needs of diverse stakeholders, including investors, consumers, regulators, and internal corporate sustainability teams, offering both an overview and detailed insights into ESG performance.


### 9. How can we integrate external data sources, such as news articles or social media, into the ESG performance evaluation?
To be more comprehensive, we can include sentiment scores from news and social media and discrepancy flags for mismatches between company-reported data and external sources.
This involves web scraping to retrieve relevant articles, sentiment analysis using NLP models, and topic modeling to identify ESG-related themes. External sentiment trends are compared with internal ESG metrics across time, identifying negative sentiment spikes, reporting gaps, and potential greenwashing risks.
This approach enhances risk management by allowing companies to detect discrepancies early, preventing regulatory scrutiny or public backlash. It also helps validate internal ESG claims with external data, boosting stakeholder trust.


### 10. How can we measure the long-term impact of ESG performance on company sustainability and financial outcomes?
To measure the long-term impact of ESG performance on company sustainability and financial outcomes, we analyze trends in ROA, ROE, and stock growth—key indicators of profitability and market performance. ESG performance is assessed using overall ESG scores to benchmark financial impact.
Due to the recent adoption of ESG reporting, time series predictions are limited by a lack of historical data. Thus, our current model, based on limited ESG disclosures, uses simple linear regression instead to capture the relationship between ESG scores and financial performance. 
Separately, Recursive Feature Elimination (RFE) helps identify the most influential ESG drivers for financial outcomes. Currently, anti-corruption training has emerged as a key ESG factor in the banking sector based on the available data. As more ESG data becomes available, model accuracy will improve, enabling companies to better assess the financial impact of ESG compliance and refine their sustainability strategies.


## Insights and Business Impact
Our platform provides insights into company ESG performance, helping businesses align with global sustainability goals, mitigate risks, and unlock competitive advantages. It guides investors by comparing ESG data across companies and countries to minimize greenwashing.
Key findings from our project include:
- Poor ESG performance increases financial and operational risks, as lower ESG scores correlate with lower ROA, suggesting inefficient asset use. Companies with low ESG scores should reassess their asset utilization strategies to improve ESG compliance and reduce operational risks.
- Anti-corruption training, particularly in the banking sector, can improve ESG scores, reducing risks, enhancing financial performance and long-term sustainability.
We conclude that investing in ESG is a competitive advantage, driving financial resilience, consumer trust, and investor confidence. Early ESG adoption can reduce legal risks and secure better market positioning. ESG influences all aspects of business performance, from revenue growth and risk management to employee retention and brand reputation.


## Recommendations
To enhance the accuracy and scalability of our ESG impact analysis, we propose the following actionable improvements:
- Expand ESG Metrics & Frameworks: Integrate additional frameworks like GRI other than SGX and include metrics such as financial risk exposure, climate risk, racial demographics, and employee well-being for a more comprehensive evaluation.
- Incorporate Third-Party & Alternative Data Sources: Integrate external validation points like news sentiment analysis, social media and regulatory filings to reduce bias and provide a holistic ESG risk assessment.
- Enhance Model Complexity & Automation: Use other machine learning methods like gradient boosting rather than linear models to capture nonlinear ESG-financial relationships and to improve predictions. Automate ESG score generation using LLMs models to reduce manual effort.
- Refine ESG Scoring Criteria: Regularly assess and optimize scoring methodologies to align with evolving ESG trends and benchmark against established agencies (e.g., MSCI, Sustainalytics) for enhanced credibility.


## Conclusion & Next Steps 
Our project facilitates the automated extraction of ESG data, presenting scores and insights through a comprehensive dashboard while modeling its financial impacts.
Next Steps:
- Automate ESG report collections with scalability: Develop a robust web-scraping pipeline with the latest reports from many companies, as our current method requires a fixed URL structure.
- Develop an interactive front-end UI: Enables real-time ESG data extraction, retrieval, and on-demand insights.
- Enhance Prompt Engineering: Improves adaptability to accommodate country-specific reporting standards and varying regulatory environments
These enhancements will establish a more dynamic, scalable, and insightful ESG analysis framework, empowering businesses to make informed, data-driven sustainability decisions.
