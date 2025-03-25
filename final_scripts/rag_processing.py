from extractValues import RAG
import pandas as pd

def process_rag(df: pd.DataFrame) -> pd.DataFrame:
    print("Running RAG process on the extracted data...")
    rag_df = RAG.rag_main(df)
    return rag_df
