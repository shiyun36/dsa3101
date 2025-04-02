Refactored code into classes and modular functions to make it more maintainable, reusable and trustable. 
extract_text_company_year.py corresponds to PdfExtractor.py 
RAG.py corresponds to RAGProcessor.py 

Refactored main.py to focus only on the high-level flow, leaving the core logic to be placed in separate modules. This promotes readability, maintainability, and ease of testing.
Note that parameters within main.py must be adjusted based on the industry of the company and year of the ESG report for best results.
