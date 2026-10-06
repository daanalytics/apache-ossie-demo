# Apache Ossie + Snowflake Demo

Interactive Streamlit in Snowflake application demonstrating how **Apache Ossie** (Incubating) — the open semantic interchange specification under the Apache Software Foundation — maps to Snowflake's native Semantic Views.

## Quick Start

### 1. Create the sample data
Run `01_setup.sql` in Snowsight or SnowSQL to create:
- Database: `OSSIE_DEMO`
- Schema: `ECOMMERCE`
- Tables: `customers`, `products`, `orders`, `order_items`

### 2. Create the Semantic View
Run `02_semantic_view.sql` to create a Snowflake Semantic View that mirrors the Ossie YAML model.

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
| `02_semantic_view.sql` | Snowflake Semantic View (mirrors Ossie spec) |
| `03_deploy_streamlit.sql` | Deploy as Streamlit in Snowflake |
| `ossie_semantic_model.yaml` | Example Ossie-format semantic model |
| `streamlit_app.py` | Interactive demo application |

## What the App Demonstrates

The Streamlit app has 5 tabs:

1. **What is Ossie?** — The problem of metric inconsistency and how Ossie solves it
2. **Ossie YAML Spec** — Annotated walkthrough of the YAML format (sources, relationships, dimensions, metrics)
3. **Ossie → Snowflake Mapping** — Side-by-side comparison showing the 1:1 concept mapping
4. **Live Query Demo** — Interactive queries implementing the semantically-defined metrics
5. **The Vision** — Interoperability diagram, ASF governance, roadmap, and community links

---

## LinkedIn Post Talking Points

### Hook
> The data industry just got a shared language for metrics. Apache Ossie (Incubating) — formerly Open Semantic Interchange — defines a vendor-neutral YAML format so that "Revenue" means the same thing whether it's queried by a BI tool, an AI agent, or a SQL IDE.

### Key Messages

1. **The Problem**: Same metric, N definitions across N tools. AI agents make this worse — they hallucinate metrics when definitions are ambiguous.

2. **Ossie's Solution**: A single YAML file defines your metrics, dimensions, and relationships. Any tool can consume it. Human-readable AND machine-readable.

3. **Snowflake's Implementation**: Snowflake Semantic Views are a native implementation that aligns directly with Ossie's concepts. The mapping is nearly 1:1 (sources → DEFINE TABLE, relationships → DEFINE RELATIONSHIP, metrics → METRIC expressions).

4. **ASF Governance**: No single vendor controls this. 50+ organizations contributing. Governed by the same foundation behind Spark, Kafka, and Iceberg.

5. **AI Angle**: AI agents need reliable semantic context. Ossie makes metric definitions portable — your agent gets the same answer regardless of which platform executes the query.

6. **Converters Already Exist**: Ossie → dbt MetricFlow, Ossie → Snowflake Semantic Model, Apache Polaris → Ossie. Define once, deploy everywhere.

### Call to Action
> Check out the interactive demo I built showing the Ossie ↔ Snowflake mapping in action. Link in comments.
> 
> Join the community: ossie.apache.org | Slack: apache-ossie.slack.com

### Hashtags
`#ApacheOssie #Snowflake #SemanticLayer #DataEngineering #AI #OpenSource`

---

## Blog Post Structure (if expanding)

1. **The Metric Consistency Problem** — Why the same KPI means different things across your stack
2. **Enter Apache Ossie** — What it is, brief history (OSI → Ossie), why ASF
3. **The YAML Format** — Walkthrough of a real model (use the e-commerce example)
4. **Snowflake's Native Alignment** — How Semantic Views implement the same concepts
5. **The Converter Ecosystem** — Define once, deploy to dbt, Snowflake, Polaris
6. **Why AI Makes This Urgent** — Agents need semantic grounding, not guesswork
7. **Try It Yourself** — Link to GitHub repo with the demo code
8. **Get Involved** — ASF community resources

---

## Resources

- [Snowflake Blog: Apache Ossie Announcement](https://www.snowflake.com/en/blog/apache-ossie-open-semantic-interchange-incubator/)
- [Apache Ossie Website](https://ossie.apache.org)
- [Ossie Slack Workspace](https://join.slack.com/t/apache-ossie/shared_invite/zt-42i1xkgy8-7YQtKEDq7v~mceFmdiLhkA)
- [Snowflake Semantic Views Documentation](https://docs.snowflake.com/en/sql-reference/sql/create-semantic-view)
