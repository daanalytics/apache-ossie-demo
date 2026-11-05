# Apache Ossie + Snowflake Demo

Interactive Streamlit in Snowflake application demonstrating how **Apache Ossie** (Incubating) — the open semantic interchange specification under the Apache Software Foundation — maps to Snowflake's native Semantic Views.

## Quick Start

### 1. Create the sample data
Run `01_setup.sql` in Snowsight or SnowSQL to create:
- Database: `OSSIE_DEMO`
- Schema: `ECOMMERCE`
- Tables: `customers`, `products`, `orders`, `order_items`

### 2. Create the Semantic View
Run `02_semantic_view.sql` to create a Snowflake semantic view from the Ossie model. Status rules such as "completed orders only" are part of the metric expressions. The live queries read this view with `SEMANTIC_VIEW()`, so they name a metric instead of restating the formula.

### 3. Deploy the Streamlit app
Upload `streamlit_app.py` to a Snowflake stage and run `03_deploy_streamlit.sql`.

```bash
# Using SnowSQL:
snowsql -q "PUT file://streamlit_app.py @OSSIE_DEMO.ECOMMERCE.streamlit_stage/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
```

Then execute the CREATE STREAMLIT statement in `03_deploy_streamlit.sql`.

### 4. Deploy the Snowflake App Runtime app

The same demo is a Next.js application in `app-runtime/`. Snowflake App Runtime builds and runs it next to the data. From that directory:

```bash
cd app-runtime
snow app deploy
```

`app.yml` creates `OSSIE_DEMO.ECOMMERCE.OSSIE_DEMO_SAR` and queries with `COMPUTE_WH`. After the first deploy, run the grants in `06_deploy_app_runtime.sql`. Open the service with `snow app open`. Locally, `npm run dev` uses `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, and `SNOWFLAKE_PASSWORD`, or `~/.snowflake/connections.toml`. The first four tabs do not need a connection; **With vs Without** does.

## Files

| File | Purpose |
|------|---------|
| `01_setup.sql` | Database, tables, and sample data |
| `02_semantic_view.sql` | Snowflake semantic view; Ossie filters live in the metric expressions |
| `03_deploy_streamlit.sql` | Deploy as Streamlit in Snowflake |
| `ossie_semantic_model.yaml` | Example Ossie-format semantic model |
| `streamlit_app.py` | Interactive Streamlit demo |
| `app-runtime/` | The same demo as a Snowflake App Runtime (Next.js) service |
| `06_deploy_app_runtime.sql` | Usage grants after `snow app deploy` |
| `recording/record_demo.py` | Browser walkthrough that saves a video of all five tabs |

## What the App Demonstrates

The Streamlit app has 5 tabs:

1. **What is Ossie?** — The problem of metric inconsistency and how Ossie solves it
2. **Ossie YAML Spec** — Annotated walkthrough of the YAML format (sources, relationships, dimensions, metrics)
3. **Ossie → Snowflake Mapping** — Side-by-side comparison showing the 1:1 concept mapping
4. **With vs Without** — The same question against the base tables and against the semantic view
5. **The Vision** — Interoperability diagram, ASF governance, roadmap, and community links

---

## Record a walkthrough

The app runs inside Streamlit in Snowflake, so the recording drives the deployed app in a browser. Copy the app URL from the address bar in Snowsight, or from `SHOW STREAMLITS` in `03_deploy_streamlit.sql`.

```bash
python3 -m venv .venv
.venv/bin/pip install -r recording/requirements.txt
.venv/bin/playwright install chromium
.venv/bin/python recording/record_demo.py --url "https://app.snowflake.com/..."
```

Sign in when the window opens, wait until the app is visible, then press Enter in the terminal. The script visits every tab, every YAML section, and every comparison question. The `.webm` file is written to `recording/output/`. The next run reuses the saved login in `recording/.browser-profile/`.

## Resources

- [Snowflake Blog: Apache Ossie Announcement](https://www.snowflake.com/en/blog/apache-ossie-open-semantic-interchange-incubator/)
- [Apache Ossie Website](https://ossie.apache.org)
- [Ossie Slack Workspace](https://join.slack.com/t/apache-ossie/shared_invite/zt-42i1xkgy8-7YQtKEDq7v~mceFmdiLhkA)
- [Snowflake Semantic Views Documentation](https://docs.snowflake.com/en/sql-reference/sql/create-semantic-view)
