
CREATE TABLE esg_text_table (
    "company" VARCHAR,
    "year" int,
    "country" VARCHAR,
    "industry" VARCHAR,
    "esg_text" VARCHAR,
    "labels" VARCHAR
);

CREATE TABLE region_table (
    "country" VARCHAR,
    "region" VARCHAR,
    "subregion" VARCHAR
);

CREATE TABLE stocks_table (
    "company" VARCHAR,
    "date" DATE,
    "close" FLOAT
);

CREATE TABLE roa_roe_table (
    "company" VARCHAR,
    "date" DATE,
    "roa" FLOAT,
    "roe" FLOAT
);


CREATE TABLE company_ticker (
    "symbol" TEXT,
    "company_name" TEXT
);

CREATE TABLE esg_rag_table (
    "company" VARCHAR,
    "year" int,
    "topic" TEXT,
    "extracted_values" TEXT,
    "final_score" FLOAT
)

-- CREATE TABLE esg_vectorDB (
--     doc_id VARCHAR,
--     doc_text TEXT,
--     metadatas JSONB
-- )
-- CREATE TABLE "esg_llm" (
--     "company" VARCHAR   NOT NULL,
--     "year" int   NOT NULL,
--     "ticker" VARCHAR,
--     "industry" VARCHAR   NOT NULL,
--     "esg_cat" VARCHAR,
--     "esg_subcat" VARCHAR,
--     "sentence_type" VARCHAR   NOT NULL,
--     "esg_framework" VARCHAR,
--     "raw_score" int   NOT NULL,
--     "esg_risk_prediction" float   NOT NULL,
--     "summarized_sentences_data" TEXT   NOT NULL,
--     "relevance_score" VARCHAR   NOT NULL
-- );