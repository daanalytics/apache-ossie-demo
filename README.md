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

## Files

| File | Purpose |
|------|---------|
| `01_setup.sql` | Database, tables, and sample data |
| `02_semantic_view.sql` | Snowflake semantic view; Ossie filters live in the metric expressions |
| `03_deploy_streamlit.sql` | Deploy as Streamlit in Snowflake |
| `ossie_semantic_model.yaml` | Example Ossie-format semantic model |
| `streamlit_app.py` | Interactive demo application |

## What the App Demonstrates

The Streamlit app has 5 tabs:

1. **What is Ossie?** — The problem of metric inconsistency and how Ossie solves it
2. **Ossie YAML Spec** — Annotated walkthrough of the YAML format (sources, relationships, dimensions, metrics)
3. **Ossie → Snowflake Mapping** — Side-by-side comparison showing the 1:1 concept mapping
4. **With vs Without** — The same question against the base tables and against the semantic view
5. **The Vision** — Interoperability diagram, ASF governance, roadmap, and community links

---

## Resources

- [Snowflake Blog: Apache Ossie Announcement](https://www.snowflake.com/en/blog/apache-ossie-open-semantic-interchange-incubator/)
- [Apache Ossie Website](https://ossie.apache.org)
- [Ossie Slack Workspace](https://join.slack.com/t/apache-ossie/shared_invite/zt-42i1xkgy8-7YQtKEDq7v~mceFmdiLhkA)
- [Snowflake Semantic Views Documentation](https://docs.snowflake.com/en/sql-reference/sql/create-semantic-view)
