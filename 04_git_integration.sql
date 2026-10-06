/*=============================================================================
  Apache Ossie + Snowflake Demo — Git Repository Integration
  
  Sets up the Snowflake objects needed to create a Workspace from the
  GitHub repository: https://github.com/daanalytics/apache-ossie-demo
  
  This creates:
    1. API Integration for GitHub (allows Snowflake to reach github.com)
    2. Git Repository object pointing to the repo
  
  After running this script you can create a Workspace in Snowsight:
    Projects » Workspaces » + » From Git Repository
    → Select the integration and repository created here
  
  Run as ACCOUNTADMIN (or a role with CREATE INTEGRATION privileges).
=============================================================================*/

USE ROLE ACCOUNTADMIN;
USE DATABASE OSSIE_DEMO;
USE SCHEMA ECOMMERCE;

-- =========================================================================
-- 1. API INTEGRATION — Allows Snowflake to connect to GitHub
-- =========================================================================
CREATE OR REPLACE API INTEGRATION github_api_integration
  API_PROVIDER = GIT_HTTPS_API
  API_ALLOWED_PREFIXES = ('https://github.com/daanalytics')
  ENABLED = TRUE
  COMMENT = 'API integration for GitHub - daanalytics repos';

-- Verify the integration
DESCRIBE API INTEGRATION github_api_integration;

-- =========================================================================
-- 2. GIT REPOSITORY — Points to the Apache Ossie demo repo
-- =========================================================================
CREATE OR REPLACE GIT REPOSITORY apache_ossie_demo_repo
  API_INTEGRATION = github_api_integration
  ORIGIN = 'https://github.com/daanalytics/apache-ossie-demo.git'
  COMMENT = 'Apache Ossie + Snowflake demo repository';

-- Fetch the latest from the remote
ALTER GIT REPOSITORY apache_ossie_demo_repo FETCH;

-- Verify: list branches
SHOW GIT BRANCHES IN apache_ossie_demo_repo;

-- Verify: list files on main branch
LS @apache_ossie_demo_repo/branches/main/;

-- =========================================================================
-- 3. GRANT ACCESS to the demo role
-- =========================================================================
GRANT USAGE ON INTEGRATION github_api_integration TO ROLE OSSIE_DEMO_ROLE;
GRANT READ ON GIT REPOSITORY OSSIE_DEMO.ECOMMERCE.apache_ossie_demo_repo TO ROLE OSSIE_DEMO_ROLE;

-- =========================================================================
-- 4. WORKSPACE SETUP (for reference — done in Snowsight UI)
-- =========================================================================
-- In Snowsight:
--   1. Go to Projects » Workspaces
--   2. Click "+" » "From Git Repository"
--   3. Repository URL: https://github.com/daanalytics/apache-ossie-demo.git
--   4. Repository name: apache_ossie_demo_repo (or pick a new name)
--   5. Integration: github_api_integration
--   6. Database and schema: OSSIE_DEMO.ECOMMERCE
--   7. Click "Create"
--
-- The workspace will sync with the Git repo and contain all demo files.
