/*=============================================================================
  Apache Ossie + Snowflake Demo — Native Ossie import, hierarchy test

  Companion to the blog post "Hierarchies in a world without hierarchies".
  Tests what SYSTEM$CREATE_SEMANTIC_VIEW_FROM_OSSIE_YAML (Preview) keeps of
  the three hierarchy techniques, compared with the offline converter:

    A. one dataset per level, chained by relationships
    B. level metadata in description / ai_context
    C. explicit hierarchy in custom_extensions

  Also checks:
    - the leaf-level gotcha (field without a dimension block -> fact)
    - whether a 0.2.0.dev0 document is rejected (docs: only 0.1.1 supported)
    - what survives a round trip via SYSTEM$READ_OSSIE_YAML_FROM_SEMANTIC_VIEW

  Prerequisites: 00_user_role_setup.sql, 01_setup.sql (OSSIE_DEMO exists)
=============================================================================*/

USE ROLE SYSADMIN;
USE WAREHOUSE OSSIE_DEMO_WH;
CREATE SCHEMA IF NOT EXISTS OSSIE_DEMO.RETAIL;
USE SCHEMA OSSIE_DEMO.RETAIL;

-- =========================================================================
-- 1. SAMPLE STAR: Product hierarchy (3 levels) + Calendar
-- =========================================================================
CREATE OR REPLACE TABLE dim_category (
    category_id   INT,
    category_name VARCHAR
);

CREATE OR REPLACE TABLE dim_subcategory (
    subcategory_id   INT,
    subcategory_name VARCHAR,
    category_id      INT
);

CREATE OR REPLACE TABLE dim_product (
    product_id     INT,
    product_name   VARCHAR,
    subcategory_id INT
);

CREATE OR REPLACE TABLE dim_date (
    date_id       INT,
    calendar_date DATE
);

CREATE OR REPLACE TABLE fct_sales (
    sale_id    INT,
    product_id INT,
    date_id    INT,
    amount     NUMBER(10,2)
);

INSERT INTO dim_category VALUES (1, 'Bikes'), (2, 'Accessories');

INSERT INTO dim_subcategory VALUES
(10, 'Road Bikes', 1),
(11, 'Mountain Bikes', 1),
(20, 'Helmets', 2);

INSERT INTO dim_product VALUES
(100, 'Road-150', 10),
(101, 'Road-250', 10),
(110, 'Mountain-100', 11),
(200, 'Sport-100 Helmet', 20);

INSERT INTO dim_date
SELECT ROW_NUMBER() OVER (ORDER BY d), d
FROM (SELECT DATEADD(day, SEQ4(), '2026-01-01'::DATE) AS d
      FROM TABLE(GENERATOR(ROWCOUNT => 365)));

INSERT INTO fct_sales VALUES
(1, 100, 10,  3500.00),
(2, 101, 40,  2400.00),
(3, 110, 95,  3300.00),
(4, 200, 120,   35.00),
(5, 100, 200, 3500.00),
(6, 110, 300, 3300.00);

-- =========================================================================
-- 2. NATIVE IMPORT — version 0.1.1 (the only version the docs list)
-- =========================================================================
-- Field ai_context, custom_extensions (Technique C) and the model-level
-- ai_context are included on purpose, to see where they end up.
-- calendar_date has no dimension block on purpose (leaf-level gotcha).
CALL SYSTEM$CREATE_SEMANTIC_VIEW_FROM_OSSIE_YAML(
  'OSSIE_DEMO.RETAIL',
  $$
  version: "0.1.1"
  name: sv_retail_hierarchies_native
  description: "Retail sales with Product and Calendar hierarchies"
  ai_context:
    instructions: "Hierarchies: Product = category_name > subcategory_name > product_name. Calendar = calendar_year > calendar_month > calendar_date."
  datasets:
    - name: sales
      source: OSSIE_DEMO.RETAIL.FCT_SALES
      primary_key: [sale_id]
      fields:
        - name: sale_id
          expression: {dialects: [{dialect: SNOWFLAKE, expression: sale_id}]}
          dimension: {is_time: false}
        - name: product_id
          expression: {dialects: [{dialect: SNOWFLAKE, expression: product_id}]}
          dimension: {is_time: false}
        - name: date_id
          expression: {dialects: [{dialect: SNOWFLAKE, expression: date_id}]}
          dimension: {is_time: false}
        - name: amount
          expression: {dialects: [{dialect: SNOWFLAKE, expression: amount}]}

    - name: product
      source: OSSIE_DEMO.RETAIL.DIM_PRODUCT
      primary_key: [product_id]
      description: "Level 3 (leaf) of the Product hierarchy"
      custom_extensions:
        - vendor_name: DAANALYTICS
          data: '{"hierarchies":[{"name":"Product","levels":["category.category_name","subcategory.subcategory_name","product.product_name"]}]}'
      fields:
        - name: product_id
          expression: {dialects: [{dialect: SNOWFLAKE, expression: product_id}]}
          dimension: {is_time: false}
        - name: subcategory_id
          expression: {dialects: [{dialect: SNOWFLAKE, expression: subcategory_id}]}
          dimension: {is_time: false}
        - name: product_name
          expression: {dialects: [{dialect: SNOWFLAKE, expression: product_name}]}
          dimension: {is_time: false}
          ai_context:
            instructions: "Product hierarchy level 3 of 3. Parent: subcategory.subcategory_name"
            synonyms: ["product", "SKU", "item"]

    - name: subcategory
      source: OSSIE_DEMO.RETAIL.DIM_SUBCATEGORY
      primary_key: [subcategory_id]
      description: "Level 2 of the Product hierarchy"
      fields:
        - name: subcategory_id
          expression: {dialects: [{dialect: SNOWFLAKE, expression: subcategory_id}]}
          dimension: {is_time: false}
        - name: category_id
          expression: {dialects: [{dialect: SNOWFLAKE, expression: category_id}]}
          dimension: {is_time: false}
        - name: subcategory_name
          expression: {dialects: [{dialect: SNOWFLAKE, expression: subcategory_name}]}
          dimension: {is_time: false}
          ai_context:
            instructions: "Product hierarchy level 2 of 3. Parent: category.category_name"

    - name: category
      source: OSSIE_DEMO.RETAIL.DIM_CATEGORY
      primary_key: [category_id]
      description: "Level 1 (top) of the Product hierarchy"
      fields:
        - name: category_id
          expression: {dialects: [{dialect: SNOWFLAKE, expression: category_id}]}
          dimension: {is_time: false}
        - name: category_name
          expression: {dialects: [{dialect: SNOWFLAKE, expression: category_name}]}
          dimension: {is_time: false}
          ai_context:
            instructions: "Product hierarchy level 1 of 3 (top)"

    - name: calendar
      source: OSSIE_DEMO.RETAIL.DIM_DATE
      primary_key: [date_id]
      fields:
        - name: date_id
          expression: {dialects: [{dialect: SNOWFLAKE, expression: date_id}]}
          dimension: {is_time: false}
        - name: calendar_year
          expression: {dialects: [{dialect: SNOWFLAKE, expression: "YEAR(calendar_date)"}]}
          dimension: {is_time: true}
        - name: calendar_month
          expression: {dialects: [{dialect: SNOWFLAKE, expression: "TO_CHAR(calendar_date, 'YYYY-MM')"}]}
          dimension: {is_time: true}
        - name: calendar_date
          expression: {dialects: [{dialect: SNOWFLAKE, expression: calendar_date}]}

  relationships:
    - {name: sales_to_product,   from: sales,       to: product,     from_columns: [product_id],     to_columns: [product_id]}
    - {name: product_to_subcat,  from: product,     to: subcategory, from_columns: [subcategory_id], to_columns: [subcategory_id]}
    - {name: subcat_to_category, from: subcategory, to: category,    from_columns: [category_id],    to_columns: [category_id]}
    - {name: sales_to_calendar,  from: sales,       to: calendar,    from_columns: [date_id],        to_columns: [date_id]}

  metrics:
    - name: total_sales
      description: "Sum of sales amount"
      expression: {dialects: [{dialect: SNOWFLAKE, expression: "SUM(sales.amount)"}]}
  $$
);

-- =========================================================================
-- 3. INSPECT THE RESULT
-- =========================================================================
-- Check 1: is calendar_date a FACT (gotcha) or a DIMENSION?
-- Check 2: do the level descriptions and synonyms appear as COMMENT / SYNONYMS?
DESCRIBE SEMANTIC VIEW sv_retail_hierarchies_native;

-- Check 3: where did ai_context.instructions and custom_extensions go?
-- Docs: "preserved in the view's extension metadata".
SELECT SYSTEM$READ_YAML_FROM_SEMANTIC_VIEW('OSSIE_DEMO.RETAIL.SV_RETAIL_HIERARCHIES_NATIVE');

-- Check 4: does the Ossie round trip return them unchanged?
SELECT SYSTEM$READ_OSSIE_YAML_FROM_SEMANTIC_VIEW('OSSIE_DEMO.RETAIL.SV_RETAIL_HIERARCHIES_NATIVE');

-- Check 5: the hierarchy works as a join chain
SELECT * FROM SEMANTIC_VIEW(
  OSSIE_DEMO.RETAIL.SV_RETAIL_HIERARCHIES_NATIVE
  DIMENSIONS category.category_name, subcategory.subcategory_name
  METRICS total_sales
)
ORDER BY category_name, total_sales DESC;

-- =========================================================================
-- 4. VERSION CHECK — the blog model uses spec version 0.2.0.dev0
-- =========================================================================
-- Expected (per docs): error listing the supported versions.
CALL SYSTEM$CREATE_SEMANTIC_VIEW_FROM_OSSIE_YAML(
  'OSSIE_DEMO.RETAIL',
  $$
  version: "0.2.0.dev0"
  name: sv_version_check
  datasets:
    - name: category
      source: OSSIE_DEMO.RETAIL.DIM_CATEGORY
      primary_key: [category_id]
      fields:
        - name: category_name
          expression: {dialects: [{dialect: SNOWFLAKE, expression: category_name}]}
          dimension: {is_time: false}
  $$
);

-- =========================================================================
-- 5. CLEANUP (optional)
-- =========================================================================
-- DROP SEMANTIC VIEW IF EXISTS OSSIE_DEMO.RETAIL.SV_RETAIL_HIERARCHIES_NATIVE;
-- DROP SCHEMA IF EXISTS OSSIE_DEMO.RETAIL;
