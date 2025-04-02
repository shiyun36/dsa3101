import argparse
import os
import pickle
from final_scripts.PdfExtractor import PDFExtractor
from final_scripts.RAGProcessor import ESGAnalyzer
from final_scripts.WikiInforProcessor import CompanyInfoUpdater
from final_scripts.db_operations import connect_to_database, insert_esg_rag_data, insert_esg_text_data, insert_wiki_data
from final_scripts.ESGScoringProcessor import ESGRAGDataframeConverter
from final_scripts.financial import financial
from final_scripts.GeneratePdfs import GeneratePdfs
from final_scripts.financial_model_powerbi import run_financial_model

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
GPT_API_KEY = os.getenv("GPT_API_KEY") ##If changing RAG to class, can input GPT_API_KEY in the variables. 
#YEARS = [2024, 2023, 2022, 2021]
URL_OUTPUT_FILE="../outputs/pdf_links_others.txt"

########### ADJUST YOUR INPUTS HERE #############
INDUSTRY = 'health'
INSERT_URL= ['https://www.fullertonhealth.com/wp-content/uploads/2024/06/FullertonHealthSustainabilityReportFY2022.pdf',
'https://www.fullertonhealth.com/wp-content/uploads/2024/09/Fullerton-Health-Sustainability-Report-FY2023.pdf' 
 ]
#Input_file = False
YEARS = [2022, 2023]
GEOGRAPHICAL_REGION = 'Singapore'
#INSERT_URL = None
#"https://investor.econhealthcare.com/misc/sr2024.pdf"
#################################################

def main():
    # Setup argparse to receive the URL
    parser = argparse.ArgumentParser(description="Extract ESG data from a PDF report URL")
    parser.add_argument("--url", type=str, help="PDF URL of tshe sustainability report")
    parser.add_argument("--country", type=str, help="Country the company is based in")
    parser.add_argument("--industry", type=str, help="Industry the company belongs to")
    args = parser.parse_args()

    # Database connection string
      # Use environment variables for sensitive info

    # Connect to the database
    conn = connect_to_database(DATABASE_URL)
    if conn:
        if args.url:
             arg_url = args.url.split(",") #so it can accept list
             arg_region = args.country #only one country    
             arg_industry = args.industry #only one industry
             pdf_extractor = PDFExtractor(saved_url_file = URL_OUTPUT_FILE, 
                     INSERT_URL = arg_url,
                     geographical_region = arg_region, 
                     industry = arg_industry)
             text_df = pdf_extractor.process_pdf()
        if INSERT_URL == "":
         
             ##### Step 0: Generate pdf links that will be extracted  #####
             pdf_links_generator = GeneratePdfs(output_file=URL_OUTPUT_FILE, 
                                             log_file = "./loggings/pdf_scraper.log",
                                             years = YEARS,
                                             industry = INDUSTRY, 
                                             geographical_region = GEOGRAPHICAL_REGION,
                                             GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")) 
             pdf_links_generator.run()
             ##### Step 1: Extract ESG text from pdf links #####
             pdf_extractor = PDFExtractor(saved_url_file = URL_OUTPUT_FILE, 
                                         INSERT_URL = INSERT_URL,
                                         geographical_region = GEOGRAPHICAL_REGION, 
                                         industry = INDUSTRY)
             text_df = pdf_extractor.process_pdf()
        
        else:
            #### Step 1: Extract ESG text from pdf links #####
            print("Step 1: Extract ESG text from pdf links")
            pdf_extractor = PDFExtractor(saved_url_file = URL_OUTPUT_FILE, 
                                        INSERT_URL = INSERT_URL,
                                        geographical_region = GEOGRAPHICAL_REGION, 
                                        industry = INDUSTRY)
            text_df = pdf_extractor.process_pdf()

            with open('text_df_fullerton.pkl', 'wb') as f:
                pickle.dump(text_df, f)
                    
            # if os.path.exists('text_df_carousell.pkl'):
            #         with open('text_df_carousell.pkl', 'rb') as f:
            #             text_df = pickle.load(f) 
            # print('load pickle file')

        if text_df.empty:
            print("No ESG text extracted. Skipping processing.")
        else:
            
            ##### Step 2: Process RAG #####
            print("2a. Processing RAG")
            esg_analysis = ESGAnalyzer(esg_text_df=text_df)
            rag_path, no_of_dups = esg_analysis.rag_main()
            print(str(rag_path))

            
            # Converting RAG dataframe to match esg_rag_table schema
            print("2b. Converting RAG dataframe")
            esg_rag_df = ESGRAGDataframeConverter(csv_path=rag_path, num_companies=no_of_dups)
            final_push_df = esg_rag_df.convert()
            print(final_push_df)
            
            # run the wiki fn
            print("2c. Run the wiki function")
            updater = CompanyInfoUpdater(saved_url_df=text_df)
            missing_rows_df = updater.form_supabase_input(text_df)


            ##### Step 3: Insert data into database #####
            print("3.Insert data into database")
            insert_wiki_data(missing_rows_df) 
            insert_esg_rag_data(final_push_df)
            insert_esg_text_data(text_df)

            ##### Step 4: Call financial function to insert financial data into database and run financial model #####
            print("4. Call financial functions and insert financial data into database")
            financial() 
            run_financial_model()
                

        # Close the connection
        conn.close()

if __name__ == "__main__":
    main()
