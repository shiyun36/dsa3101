
CREATE TABLE IF NOT EXISTS esg_text_table (
    "company" VARCHAR,
    "year" int,
    "country" VARCHAR,
    "industry" VARCHAR,
    "esg_text" VARCHAR
);

CREATE TABLE IF NOT EXISTS region_table (
    "country" VARCHAR,
    "region" VARCHAR,
    "subregion" VARCHAR
);

CREATE TABLE IF NOT EXISTS stocks_table (
    "company" VARCHAR,
    "date" DATE,
    "close" FLOAT
);

CREATE TABLE IF NOT EXISTS roa_roe_table (
    "company" VARCHAR,
    "date" DATE,
    "roa" FLOAT,
    "roe" FLOAT
);

CREATE TABLE IF NOT EXISTS company_ticker (
    "symbol" TEXT,
    "company_name" TEXT
);

CREATE TABLE IF NOT EXISTS esg_rag_table (
    "company" VARCHAR,
    "industry" VARCHAR,
    "country" VARCHAR,
    "year" int,
    "topic" TEXT,
    "extracted_values" TEXT,
    "final_score" FLOAT
)