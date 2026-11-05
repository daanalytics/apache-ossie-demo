/*=============================================================================
  Apache Ossie + Snowflake Demo — Snowflake App Runtime

  The application service is created by the Snowflake CLI, not by this script.
  From the app-runtime directory:

      snow app deploy

  That reads app-runtime/app.yml and creates:

      OSSIE_DEMO.ECOMMERCE.OSSIE_DEMO_SAR

  Prerequisites: 01_setup.sql and 02_semantic_view.sql. The query warehouse
  in app.yml is COMPUTE_WH, the same warehouse the Streamlit app uses.

  Run the grants below after the first successful deploy.
=============================================================================*/

USE ROLE ACCOUNTADMIN;

GRANT USAGE ON APPLICATION SERVICE OSSIE_DEMO.ECOMMERCE.OSSIE_DEMO_SAR TO ROLE OSSIE_DEMO_ROLE;
GRANT USAGE ON APPLICATION SERVICE OSSIE_DEMO.ECOMMERCE.OSSIE_DEMO_SAR TO ROLE PUBLIC;
