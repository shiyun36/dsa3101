import argparse
import os
from final_scripts.PdfExtractor import PDFExtractor
from final_scripts.RAGProcessor import ESGAnalyzer
from final_scripts.db_operations import connect_to_database, insert_esg_rag_data, insert_esg_text_data
from final_scripts.ESGScoringProcessor import ESGRAGDataframeConverter
#from financial import financial
from final_scripts.GeneratePdfs import GeneratePdfs

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
GPT_API_KEY = os.getenv("GPT_API_KEY") ##If changing RAG to class, can input GPT_API_KEY in the variables. 
GEOGRAPHICAL_REGION = 'Singapore'
INDUSTRY = 'finance'
YEARS = [2024, 2023, 2022, 2021]
URL_OUTPUT_FILE="../outputs/pdf_links.txt"

def main():
    # Setup argparse to receive the URL
    parser = argparse.ArgumentParser(description="Extract ESG data from a PDF report URL")
    parser.add_argument("--url", type=str, help="PDF URL of the sustainability report")
    parser.add_argument("--country", type=str, help="Country the company is based in")
    parser.add_argument("--industry", type=str, help="Industry the company belongs to")
    args = parser.parse_args()

    # If run without CLI args, fallback to defaults
    if not any(vars(args).values()):
        args.url = "https://cdn.sea.com/webmain/static/resource/seagroup/Sustainability/Social%20Impact%20reports/Sea%20Sustainability%20Report%202022_1.pdf"
        args.country = "singapore"
        args.industry = "finance"

    # Database connection string
      # Use environment variables for sensitive info

    # Connect to the database
    conn = connect_to_database(DATABASE_URL)
    if conn:
        
        ##### Step 0: Generate pdf links that will be extracted  #####
        pdf_links_generator = GeneratePdfs(output_file=URL_OUTPUT_FILE, 
                                           log_file = "./loggings/pdf_scraper.log",
                                           years =YEARS,
                                           industry = INDUSTRY, 
                                           geographical_region = GEOGRAPHICAL_REGION,
                                           GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")) 
        pdf_links_generator.run()
        
        ##### Step 1: Extract ESG text from pdf links #####
        pdf_extractor = PDFExtractor(saved_url_file = URL_OUTPUT_FILE, 
                                     geographical_region = GEOGRAPHICAL_REGION, 
                                     industry = INDUSTRY)
        text_df = pdf_extractor.process_pdf()  
        print(text_df)

        if text_df.empty:
            print("No ESG text extracted. Skipping processing.")
        else:
            
            ##### Step 2: Process RAG #####
            print("ireach before analyzer")
            esg_analysis = ESGAnalyzer(esg_text_df=text_df)
            rag_path = esg_analysis.rag_main()
            print(str(rag_path))

            # Converting RAG dataframe to match esg_rag_table schema
            esg_rag_df = ESGRAGDataframeConverter(csv_path=rag_path)
            final_push_df = esg_rag_df.convert()            

            ##### Step 3: Insert data into database #####
            insert_esg_rag_data(final_push_df)
            insert_esg_text_data(final_push_df)

            ##### Step 4: Call financial function to insert financial data into database #####
            #financial() 

        # Close the connection
        conn.close()

if __name__ == "__main__":
    main()
