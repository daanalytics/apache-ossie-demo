/*=============================================================================
  Apache Ossie + Snowflake Demo — User & Role Setup
  
  Creates a dedicated demo user with a custom role that grants access to:
    - The OSSIE_DEMO database and ECOMMERCE schema
    - All tables (customers, products, orders, order_items)
    - The Semantic View (ecommerce_semantic_model)
    - The Streamlit application (ossie_demo_app)
    - A dedicated warehouse for compute
  
  Run as ACCOUNTADMIN or a role with CREATE USER / CREATE ROLE / CREATE WAREHOUSE.
=============================================================================*/

USE ROLE ACCOUNTADMIN;

-- =========================================================================
-- 1. WAREHOUSE
-- =========================================================================
CREATE WAREHOUSE IF NOT EXISTS OSSIE_DEMO_WH
  WAREHOUSE_SIZE = 'X-SMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Warehouse for the Apache Ossie demo';

-- =========================================================================
-- 2. ROLE
-- =========================================================================
CREATE ROLE IF NOT EXISTS OSSIE_DEMO_ROLE
  COMMENT = 'Role for the Apache Ossie + Snowflake demo application';

-- Grant role to SYSADMIN so it stays in the standard hierarchy
GRANT ROLE OSSIE_DEMO_ROLE TO ROLE SYSADMIN;

-- =========================================================================
-- 3. WAREHOUSE GRANTS
-- =========================================================================
GRANT USAGE ON WAREHOUSE OSSIE_DEMO_WH TO ROLE OSSIE_DEMO_ROLE;
GRANT OPERATE ON WAREHOUSE OSSIE_DEMO_WH TO ROLE OSSIE_DEMO_ROLE;

-- =========================================================================
-- 4. DATABASE & SCHEMA GRANTS
-- =========================================================================
GRANT USAGE ON DATABASE OSSIE_DEMO TO ROLE OSSIE_DEMO_ROLE;
GRANT USAGE ON SCHEMA OSSIE_DEMO.ECOMMERCE TO ROLE OSSIE_DEMO_ROLE;

-- Tables: SELECT on all current and future tables
GRANT SELECT ON ALL TABLES IN SCHEMA OSSIE_DEMO.ECOMMERCE TO ROLE OSSIE_DEMO_ROLE;
GRANT SELECT ON FUTURE TABLES IN SCHEMA OSSIE_DEMO.ECOMMERCE TO ROLE OSSIE_DEMO_ROLE;

-- Views: SELECT on all current and future views
GRANT SELECT ON ALL VIEWS IN SCHEMA OSSIE_DEMO.ECOMMERCE TO ROLE OSSIE_DEMO_ROLE;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA OSSIE_DEMO.ECOMMERCE TO ROLE OSSIE_DEMO_ROLE;

-- Semantic Views
GRANT SELECT ON ALL SEMANTIC VIEWS IN SCHEMA OSSIE_DEMO.ECOMMERCE TO ROLE OSSIE_DEMO_ROLE;
GRANT SELECT ON FUTURE SEMANTIC VIEWS IN SCHEMA OSSIE_DEMO.ECOMMERCE TO ROLE OSSIE_DEMO_ROLE;

-- Stages (for Streamlit file access)
GRANT READ ON ALL STAGES IN SCHEMA OSSIE_DEMO.ECOMMERCE TO ROLE OSSIE_DEMO_ROLE;

-- Streamlit and Agent grants: see 05_app_agent_grants.sql
-- (run after those objects have been created)

-- =========================================================================
-- 5. USER
-- =========================================================================
CREATE USER IF NOT EXISTS AWS_USW_DAANALYTICS_BLOG_OSSIE_DEMO
  PASSWORD = 'OssieDemo2026!'
  DEFAULT_ROLE = OSSIE_DEMO_ROLE
  DEFAULT_WAREHOUSE = OSSIE_DEMO_WH
  DEFAULT_NAMESPACE = OSSIE_DEMO.ECOMMERCE
  MUST_CHANGE_PASSWORD = TRUE
  COMMENT = 'Demo user for the Apache Ossie + Snowflake demo';

GRANT ROLE OSSIE_DEMO_ROLE TO USER AWS_USW_DAANALYTICS_BLOG_OSSIE_DEMO;

-- =========================================================================
-- 6. VERIFY
-- =========================================================================
SHOW GRANTS TO ROLE OSSIE_DEMO_ROLE;
SHOW GRANTS TO USER AWS_USW_DAANALYTICS_BLOG_OSSIE_DEMO;
