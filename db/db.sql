
CREATE TABLE esg_bert (
    "esg_cat" VARCHAR NOT NULL,
    "sentence" TEXT NOT NULL,
    "confidence_score" FLOAT NOT NULL
);

CREATE TABLE "esg-industry-metrics" (
    "esg_cat" VARCHAR   NOT NULL,
    "esg_subcat" VARCHAR   NOT NULL,
    "industry" VARCHAR   NOT NULL,
    -- like percent to take of the score for that specific industry
    "criteria_weight" float   NOT NULL
);
--example tables to use


-- this is the actual table 
-- -- should be unique
-- CREATE TABLE "ESG-company" (
--     "company" VARCHAR   NOT NULL,
--     "year" INT   NOT NULL,
--     "esg_framework" VARCHAR   NOT NULL,
--     "total_revenue" int   NOT NULL,
--     "net_profit" int   NOT NULL,
--     "market_cap" int   NOT NULL,
--     "return_on_equity" int   NOT NULL,
--     "return_on_asset" int   NOT NULL,
--     "employee_count" int   NOT NULL,
--     -- mnc/sme?
--     "company_type" VARCHAR   NOT NULL,
--     "total_assets" int   NOT NULL,
--     "total_liabilities" int   NOT NULL,
--     "debt_to_equity_ratio" float   NOT NULL,
--     "pe_ratio" float   NOT NULL,
--     "esg_investment" float   NOT NULL,
--     "carbon_price" float   NOT NULL,
--     "esg_fines" float   NOT NULL,
--     "non_compliance_count" int   NOT NULL,
--     -- maybe we can see if longer reports are better?
--     "sentences_count" int   NOT NULL,
--     CONSTRAINT "pk_ESG-company" PRIMARY KEY (
--         "company"
--      )
-- );

-- -- we can edit this as needed from the finbert model output
-- CREATE TABLE "ESG-bert" (
--     "company" VARCHAR   NOT NULL,
--     "company_id" int   NOT NULL,
--     -- Can be stringed depending on needs but easier to filter
--     "year" int   NOT NULL,
--     "esg_cat" VARCHAR   NOT NULL,
--     "esg_subcat" VARCHAR   NOT NULL,
--     "sentence" TEXT   NOT NULL,
--     "sentiment" VARCHAR   NOT NULL,
--     -- finbert should have a score for labels iirc
--     "confidence_score" float   NOT NULL,
--     CONSTRAINT "pk_ESG-bert" PRIMARY KEY (
--         "company"
--      )
-- );

-- -- our scores -> we can compute
-- CREATE TABLE "esg-industry-metrics" (
--     "esg_cat" VARCHAR   NOT NULL,
--     "esg_subcat" VARCHAR   NOT NULL,
--     "industry" VARCHAR   NOT NULL,
--     -- like percent to take of the score for that specific industry
--     "criteria_weight" float   NOT NULL
-- );

-- CREATE TABLE "industry_avg_scores" (
--     "industry" VARCHAR   NOT NULL,
--     "esg_cat" VARCHAR   NOT NULL,
--     "esg_subcat" VARCHAR   NOT NULL,
--     -- idk maybe can be in raw number or percent
--     "industry_benchmark" float   NOT NULL,
--     "industry_avg" float   NOT NULL
-- );

-- CREATE TABLE "esg-llm(??)" (
--     "company" VARCHAR   NOT NULL,
--     "year" int   NOT NULL,
--     "industry" VARCHAR   NOT NULL,
--     "esg_cat" VARCHAR   NOT NULL,
--     "esg_subcat" VARCHAR   NOT NULL,
--     -- as in like
--     "summarized_sentences_data" TEXT   NOT NULL,
--     -- qualitative or quantitative
--     "sentence_type" VARCHAR   NOT NULL,
--     -- we can calculate this with criteria weight
--     "raw_score" int   NOT NULL,
--     "esg_risk_prediction" float   NOT NULL,
--     "summarized_sentences_data_relevance_score" float   NOT NULL
-- );

-- -- use ner on the summarized data to get stats?
-- CREATE TABLE "esg-ner" (
--     "company" VARCHAR   NOT NULL,
--     "year" int   NOT NULL,
--     "industry" VARCHAR   NOT NULL,
--     "summarized_sentences_data" text   NOT NULL,
--     "entity_type" VARCHAR   NOT NULL,
--     "statistics" int   NOT NULL,
--     "statistics_metrics" string   NOT NULL
-- );

-- CREATE TABLE "stakeholder-info" (
--     "company" VARCHAR   NOT NULL,
--     "year" int   NOT NULL,
--     "stakeholder_group" VARCHAR   NOT NULL,
--     "stakeholder_needs_id" int   NOT NULL,
--     "stakeholder_needs" TEXT   NOT NULL
-- );

-- ALTER TABLE "ESG-company" ADD CONSTRAINT "fk_ESG-company_company" FOREIGN KEY("company")
-- REFERENCES "stakeholder-info" ("company");

-- ALTER TABLE "ESG-bert" ADD CONSTRAINT "fk_ESG-bert_company" FOREIGN KEY("company")
-- REFERENCES "ESG-company" ("company");

-- ALTER TABLE "esg-industry-metrics" ADD CONSTRAINT "fk_esg-industry-metrics_industry" FOREIGN KEY("industry")
-- REFERENCES "industry_avg_scores" ("industry");

-- ALTER TABLE "esg-llm(??)" ADD CONSTRAINT "fk_esg-llm(??)_company" FOREIGN KEY("company")
-- REFERENCES "ESG-company" ("company");

-- ALTER TABLE "esg-llm(??)" ADD CONSTRAINT "fk_esg-llm(??)_industry" FOREIGN KEY("industry")
-- REFERENCES "esg-industry-metrics" ("industry");

-- ALTER TABLE "esg-ner" ADD CONSTRAINT "fk_esg-ner_summarized_sentences_data" FOREIGN KEY("summarized_sentences_data")
-- REFERENCES "esg-llm(??)" ("summarized_sentences_data");

