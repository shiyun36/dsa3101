Testing various ways to extract the ESG data from the csv from Shiyun's branch. Regex sucks so trying NLP code courtesy of ChatGPT. So far, performance seems pretty poor. 

I adjusted the csv file to leave a blank line between each company's ESG report.
Below is how the NLP + regex method is supposed to work:

How This Code Works
Combined Extraction:
– For each metric, we first try to extract the value using a regex.
– If regex extraction fails, we process the text with spaCy to look for numeric entities (labeled as CARDINAL or QUANTITY) that appear near our specified keywords.

Indicator Metrics:
– We check for the presence of certain keywords (e.g. "anti-corruption") to set binary indicators (0 or 1).

Normalization & Scoring:
– Numerical metrics are normalized from 0 to 1.
– The Environmental, Social, and Governance (E, S, G) scores are computed by averaging the corresponding metrics and then weighted equally (each pillar contributes ~3.33 points to a total of 10).

Filtering & Aggregation:
– Only rows where at least one metric or indicator is found are kept.
– A company name is extracted from each report (first by checking for a “Company:” label, then via spaCy ORG entities, or a fallback).
– The final ESG score is then averaged per company.

Output:
– The final company-level ESG scores are saved in the file Final Company ESG Scores.