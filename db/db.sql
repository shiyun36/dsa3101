
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
    );
    
    CREATE TABLE IF NOT EXISTS general_company_info_table (
        "Name" TEXT,
        "Country" TEXT,
        "Continent" TEXT,
        "Industry" TEXT,
        "Year" TEXT,
        "GHG Scope 1 emission" TEXT,
        "GHG Scope 2 emission" TEXT,
        "GHG Scope 3 emission" TEXT,
        "Water Consumption" TEXT,
        "Energy Consumption" TEXT,
        "Waste Generation" TEXT,
        "Total Employees" TEXT,
        "Total Female Employees" TEXT,
        "Employees under 30" TEXT,
        "Employees between 30-50" TEXT,
        "Employees above 50s" TEXT,
        "Fatalities" TEXT,
        "Injuries" TEXT,
        "Avg Training Hours per employee" TEXT,
        "Training Done, Independent Directors" TEXT,
        "Female Directors" TEXT,
        "Female Managers" TEXT,
        "Employees Trained" TEXT,
        "Certifications" TEXT,
        "Total Revenue" TEXT,
        "Total ESG Investment" TEXT,
        "Net Profit" TEXT,
        "Debt-Equity Ratio" TEXT,
        "ROE" TEXT,
        "ROA" TEXT,
        CONSTRAINT unique_company_info UNIQUE ("Name","Year"),
        CONSTRAINT general_info_unique_pk PRIMARY KEY ("Company","Year")
    )
