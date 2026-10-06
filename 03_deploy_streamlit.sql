/*=============================================================================
  Apache Ossie + Snowflake Demo — Deploy Streamlit in Snowflake
  
  Prerequisites:
    1. Run 01_setup.sql to create the database, schema, and sample data
    2. Run 02_semantic_view.sql to create the semantic view
    3. Upload streamlit_app.py to a stage (or use CREATE STREAMLIT ... FROM)
=============================================================================*/

USE DATABASE OSSIE_DEMO;
USE SCHEMA ECOMMERCE;

-- 1. Create a stage to hold the Streamlit app files
CREATE STAGE IF NOT EXISTS streamlit_stage
  DIRECTORY = (ENABLE = TRUE);

-- 2. Upload the Streamlit app file to the stage
-- Run this from SnowSQL or Snowsight:
-- PUT file:///path/to/streamlit_app.py @OSSIE_DEMO.ECOMMERCE.streamlit_stage/
--   AUTO_COMPRESS = FALSE OVERWRITE = TRUE;

-- 3. Create the Streamlit app object
CREATE OR REPLACE STREAMLIT OSSIE_DEMO.ECOMMERCE.ossie_demo_app
  ROOT_LOCATION = '@OSSIE_DEMO.ECOMMERCE.streamlit_stage'
  MAIN_FILE = 'streamlit_app.py'
  TITLE = 'Apache Ossie + Snowflake Demo'
  COMMENT = 'Interactive demo showing how Apache Ossie open semantic spec maps to Snowflake Semantic Views'
  QUERY_WAREHOUSE = 'COMPUTE_WH';

-- 4. Grant access (adjust role as needed)
GRANT USAGE ON STREAMLIT OSSIE_DEMO.ECOMMERCE.ossie_demo_app TO ROLE PUBLIC;

-- 5. Show the URL
SHOW STREAMLITS IN SCHEMA OSSIE_DEMO.ECOMMERCE;
