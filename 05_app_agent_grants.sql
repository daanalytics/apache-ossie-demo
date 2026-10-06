/*=============================================================================
  Apache Ossie + Snowflake Demo — App & Agent Grants
  
  Run AFTER the Streamlit app and/or Cortex Agent have been created.
  Grants the demo role access to these objects.
  
  Prerequisites:
    - 00_user_role_setup.sql (role exists)
    - 03_deploy_streamlit.sql (Streamlit app exists)
=============================================================================*/

USE ROLE ACCOUNTADMIN;

-- =========================================================================
-- 1. STREAMLIT GRANTS
-- =========================================================================
-- Run after 03_deploy_streamlit.sql has been executed
GRANT USAGE ON STREAMLIT OSSIE_DEMO.ECOMMERCE.OSSIE_DEMO_APP TO ROLE OSSIE_DEMO_ROLE;

-- =========================================================================
-- 2. CORTEX AGENT GRANTS
-- =========================================================================
-- Cortex Analyst access to the semantic view is already granted in
-- 00_user_role_setup.sql (SELECT on all semantic views).
-- If a Cortex Agent object is created, grant usage here:
-- GRANT USAGE ON CORTEX AGENT OSSIE_DEMO.ECOMMERCE.<AGENT_NAME> TO ROLE OSSIE_DEMO_ROLE;
