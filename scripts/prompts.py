def prompts(data,table_data):
    return f"""
Can you analyze the following ESG report and provide a structured summary in JSON format for each key point?

Each key point should be a grouping of related sentences under the same ESG category, ensuring clarity and coherence. The output should follow this format:

{{
  "company": "<Company Name>",
  "year": <Year>,
  "ticker": "<Ticker Symbol>", **Note**: If the ticker symbol is not provided, you need to deduce the ticker symbol based on the company name (e.g., Pfizer -> PFE).
  "industry": "<Industry>",
  "esg_category": "<ESG Category>", # Already labeled under 'cat'
  "esg_subcategory": "<ESG Subcategory>",
  "sentence_type": "<Qualitative or Quantitative>",
  "esg_framework": "<ESG Framework>",
  "raw_score": <Raw Score (1-10)>,
  "esg_risk_prediction": <Risk Prediction (0 to 1)>,
  "summarized_sentences_data": "<Detailed and structured summary of key ESG insights, ensuring all relevant statistics, numerical values, and dates are included. The summary should be **comprehensive (minimum of 3 sentences)** and explain the significance of the data, including business impacts, strategic goals, and future plans. Feel free to provide a longer and more detailed summary if necessary.>",
  "relevance_score": "<High, Medium, or Low>"
}}

### **Guidelines for Analysis:**
- **Grouping Sentences:** Combine related sentences under the same ESG category into **coherent key points** instead of listing them individually.
- **Sentence Type:** Classify each sentence as **Qualitative** (descriptive insights) or **Quantitative** (numeric/statistical data).
- **ESG Risk Prediction:** Provide a **risk score between 0 and 1**, representing the ESG risk level. This should be based on the context of the report, including trends and potential threats to ESG goals.
- **Summarized Sentences Data:**  
  - Generate a **detailed and structured summary** covering the **main insights** related to ESG strategies and performance.  
  # - The summary should include **contextual details**, such as the impact of ESG initiatives, challenges faced, and strategic decisions.  
  - **Ensure all statistics, numerical values (percentages, financial figures, impact metrics, etc.), and dates (years, reporting periods, targets, etc.) are explicitly included.**  
  - If a numerical value (e.g., "20% reduction in emissions") or a date (e.g., "by 2030") is present, it **must be retained** in the summary.  
  - When possible, **connect ESG actions to business impact** (e.g., "These efforts align with the company's sustainability goals and regulatory compliance requirements.").
- **Relevance Score:** Assign a score (**High, Medium, or Low**) based on the **importance and specificity** of the information in the ESG context.
- **Raw Score:** Extract or infer the **ESG risk score (1-10)** from available data or deduce it from related insights in the report.

### **Input Data Format:**  
The input consists of **individual sentences**, each labeled with:  
- **Sentence text**  
- **ESG subcategory**  
- **Confidence score**  
- **ESG Category**

#### **Data Input:**  
{data}

Additionally, the tables data extracted are available in json format as:  
{table_data}  *(These dataframes contain relevant numerical insights and additional context related to ESG performance, goals, and predictions.)*

Please ensure to **integrate the insights from these tables** into the overall analysis, using them to **augment and enhance** the structured summaries. If the tables contain relevant **numerical insights, performance metrics, targets, or ESG-related risks**, these should be included in the **summarized_sentences_data** for each ESG category. This will provide a comprehensive view that incorporates both sentence-based and table-based insights.

Please process the data accordingly and generate structured insights, combining the key points from both sentence-based and table-based data.
"""
