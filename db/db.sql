
    CREATE TABLE IF NOT EXISTS esg_text_table (
        "company" VARCHAR,
        "year" int,
        "country" VARCHAR,
        "industry" VARCHAR,
        "esg_text" VARCHAR
        -- CONSTRAINT unique_esg_entry UNIQUE (company, year,country,industry,esg_text)
    );

    CREATE TABLE IF NOT EXISTS region_table (
        "country" VARCHAR,
        "region" VARCHAR,
        "subregion" VARCHAR,
        CONSTRAINT unique_region_entry UNIQUE (country, region,subregion)
    );

    CREATE TABLE IF NOT EXISTS stocks_table (
        "company" VARCHAR,
        "date" DATE,
        "close" FLOAT,
        CONSTRAINT unique_stock_entry UNIQUE (company, date)
    );

    CREATE TABLE IF NOT EXISTS roa_roe_table (
        "company" VARCHAR,
        "date" DATE,
        "roa" FLOAT,
        "roe" FLOAT,
        CONSTRAINT unique_roa_roe_entry UNIQUE (company, date)
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
        "final_score" FLOAT,
        CONSTRAINT unique_esg_rag_entry UNIQUE (company,industry,country,year, topic,extracted_values,final_score),
        CONSTRAINT esg_rag_pk PRIMARY KEY (company, industry, country, year,topic)
    );

    CREATE TABLE IF NOT EXISTS esg_financial_model_top_features_table (
        "variable" VARCHAR,
        "feature" VARCHAR,
        "rank" INT
    );

    CREATE TABLE IF NOT EXISTS esg_financial_model_table (
        "esg_score" FLOAT,
        "roa_actual" FLOAT,
        "roa_predicted" FLOAT,
        "roe_actual" FLOAT,
        "roe_predicted" FLOAT,
        "stock_growth_actual" FLOAT,
        "stock_growth_predicted" FLOAT
    )