
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
    "industry" VARCHAR,
    "country" VARCHAR,
    "year" int,
    "topic" TEXT,
    "extracted_values" TEXT,
    "final_score" FLOAT
)