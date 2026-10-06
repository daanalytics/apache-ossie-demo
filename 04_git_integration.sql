/*=============================================================================
  Apache Ossie + Snowflake Demo — Git Repository Integration (Private Repo)
  
  Sets up the Snowflake objects needed to create a Workspace from the
  GitHub repository: https://github.com/daanalytics/apache-ossie-demo
  
  For bi-directional sync (commit & push from Snowsight back to GitHub),
  the repo must be private and authenticated with a Personal Access Token.
  
  This creates:
    1. Secret storing a GitHub Personal Access Token (PAT)
    2. API Integration for GitHub (allows Snowflake to reach github.com)
    3. Git Repository object pointing to the repo (with PAT auth)
    4. Grants for the demo role
  
  Prerequisites:
    - A GitHub PAT with 'repo' scope (Settings » Developer settings »
      Personal access tokens » Fine-grained tokens)
    - The repo set to Private on GitHub
  
  Run as ACCOUNTADMIN (or a role with CREATE INTEGRATION privileges).
=============================================================================*/

USE ROLE ACCOUNTADMIN;
USE DATABASE OSSIE_DEMO;
USE SCHEMA ECOMMERCE;

-- =========================================================================
-- 1. SECRET — Stores the GitHub Personal Access Token
-- =========================================================================
-- Replace <YOUR_GITHUB_PAT> with your actual GitHub PAT.
-- The PAT needs at minimum the 'repo' scope (or 'Contents: Read and write'
-- for fine-grained tokens) to enable commit/push from Snowsight.

CREATE OR REPLACE SECRET github_pat_secret
  TYPE = PASSWORD
  USERNAME = 'daanalytics'
  PASSWORD = '<YOUR_GITHUB_PAT>'
  COMMENT = 'GitHub PAT for daanalytics - used for git-synced workspaces';

-- =========================================================================
-- 2. API INTEGRATION — Allows Snowflake to connect to GitHub
-- =========================================================================
CREATE OR REPLACE API INTEGRATION github_api_integration
  API_PROVIDER = GIT_HTTPS_API
  API_ALLOWED_PREFIXES = ('https://github.com/daanalytics')
  ALLOWED_AUTHENTICATION_SECRETS = (github_pat_secret)
  ENABLED = TRUE
  COMMENT = 'API integration for GitHub - daanalytics repos (with PAT auth)';

-- Verify the integration
DESCRIBE API INTEGRATION github_api_integration;

-- =========================================================================
-- 3. GIT REPOSITORY — Points to the Apache Ossie demo repo (with auth)
-- =========================================================================
CREATE OR REPLACE GIT REPOSITORY apache_ossie_demo_repo
  API_INTEGRATION = github_api_integration
  GIT_CREDENTIALS = github_pat_secret
  ORIGIN = 'https://github.com/daanalytics/apache-ossie-demo.git'
  COMMENT = 'Apache Ossie + Snowflake demo repository (private, with push access)';

-- Fetch the latest from the remote
ALTER GIT REPOSITORY apache_ossie_demo_repo FETCH;

-- Verify: list branches
SHOW GIT BRANCHES IN apache_ossie_demo_repo;

-- Verify: list files on main branch
LS @apache_ossie_demo_repo/branches/main/;

-- =========================================================================
-- 4. GRANT ACCESS to the demo role
-- =========================================================================
GRANT USAGE ON INTEGRATION github_api_integration TO ROLE OSSIE_DEMO_ROLE;
GRANT USAGE ON SECRET OSSIE_DEMO.ECOMMERCE.github_pat_secret TO ROLE OSSIE_DEMO_ROLE;
GRANT READ ON GIT REPOSITORY OSSIE_DEMO.ECOMMERCE.apache_ossie_demo_repo TO ROLE OSSIE_DEMO_ROLE;

-- =========================================================================
-- 5. WORKSPACE SETUP (done in Snowsight UI)
-- =========================================================================
-- In Snowsight:
--   1. Go to Projects » Workspaces
--   2. Click "+" » "From Git Repository"
--   3. Repository URL: https://github.com/daanalytics/apache-ossie-demo.git
--   4. Workspace name: apache-ossie-demo
--   5. API integration: GITHUB_API_INTEGRATION
--   6. Select "Personal access token" (NOT "Public repository")
--   7. Credentials secret: OSSIE_DEMO.ECOMMERCE » github_pat_secret
--   8. Click "Create"
--
-- With PAT authentication you can commit & push changes from Snowsight
-- back to the GitHub repo (bi-directional sync).
