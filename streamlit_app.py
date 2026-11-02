"""
Apache Ossie + Snowflake Demo
==============================
Interactive Streamlit in Snowflake application demonstrating how Apache Ossie's
open semantic specification maps to Snowflake Semantic Views.

Deploy: See 03_deploy_streamlit.sql
"""

import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(
    page_title="Apache Ossie + Snowflake Demo",
    page_icon="🦘",
    layout="wide",
)

session = get_active_session()

# =============================================================================
# HEADER
# =============================================================================
st.title("🦘 Apache Ossie (Incubating) + Snowflake")
st.caption("An open specification for semantic interoperability — and how Snowflake implements it natively")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "What is Ossie?",
    "Ossie YAML Spec",
    "Ossie → Snowflake Mapping",
    "With vs Without",
    "The Vision",
])

# =============================================================================
# TAB 1: WHAT IS APACHE OSSIE?
# =============================================================================
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("The Problem: Metric Chaos")
        st.markdown("""
        Every organization faces the same challenge:
        
        > *"Monthly Active Users"* is defined **differently** in your CRM, 
        > your data warehouse, your BI tool, and your AI agent.
        
        When a human analyst or an AI agent runs a query, they shouldn't have to 
        guess which definition is correct. Yet today, the same business concept 
        lives in dozens of incompatible formats across the data stack.
        """)
        
        st.divider()
        
        st.header("The Solution: Apache Ossie")
        st.markdown("""
        **Apache Ossie** is an open specification for semantic layer and ontology. 
        It defines a **vendor-neutral YAML format** for expressing:
        
        - **Metrics** — unambiguous business measures (Revenue, AOV, Churn Rate)
        - **Dimensions** — attributes to slice and filter by (Region, Segment, Date)
        - **Relationships** — how entities connect (orders → customers → products)
        - **Business rules** — the intent and context behind the data
        
        Any tool — BI platform, query engine, or AI agent — can consume and produce 
        Ossie definitions **without loss of meaning**.
        """)
    
    with col2:
        st.markdown("### Quick Facts")
        st.metric("Contributing Organizations", "50+")
        st.metric("Commits Since Nov 2025", "100+")
        st.metric("Merged Pull Requests", "35+")
        
        st.markdown("---")
        st.markdown("### Governance")
        st.info("""
        **Apache Software Foundation**  
        Vendor-neutral, open governance.  
        No single company controls the standard.
        """)
        
        st.markdown("---")
        st.markdown("### Key Contributors")
        contributors = [
            "Snowflake", "Salesforce", "Databricks",
            "dbt Labs", "RelationalAI", "GoodData", "Honeydew"
        ]
        for c in contributors:
            st.markdown(f"- {c}")
    
    st.divider()
    
    st.subheader("Why 'Ossie'?")
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown("### 🦘")
    with col_b:
        st.markdown("""
        The project was originally named *Open Semantic Interchange (OSI)*, but was 
        renamed to avoid confusion with other open-source projects sharing that acronym.
        
        The mascot is a **kangaroo** — carrying semantic metadata in its pouch as it 
        hops between systems in the data stack.
        
        The specification and YAML format are unchanged; only the name and governance 
        home have evolved.
        """)

# =============================================================================
# TAB 2: OSSIE YAML SPEC EXPLORER
# =============================================================================
with tab2:
    st.header("Ossie YAML Specification — Annotated Example")
    st.markdown("""
    Below is a complete Ossie semantic model for an e-commerce domain. 
    This single YAML file serves as the **source of truth** that any tool can consume.
    """)
    
    section = st.radio(
        "Jump to section:",
        ["Full Model", "Sources", "Relationships", "Dimensions", "Metrics"],
        horizontal=True,
    )
    
    yaml_sources = '''sources:
  - name: orders
    description: Completed and in-progress customer orders
    database: OSSIE_DEMO
    schema: ECOMMERCE
    table: ORDERS
    primary_key: order_id
    
  - name: customers
    description: Registered customers with segmentation data
    database: OSSIE_DEMO
    schema: ECOMMERCE
    table: CUSTOMERS
    primary_key: customer_id

  - name: products
    description: Product catalog with pricing
    database: OSSIE_DEMO
    schema: ECOMMERCE
    table: PRODUCTS
    primary_key: product_id'''

    yaml_relationships = '''relationships:
  - name: order_to_customer
    description: Each order belongs to one customer
    left_source: orders
    right_source: customers
    join_type: many_to_one
    condition: "orders.customer_id = customers.customer_id"

  - name: order_item_to_order
    description: Each line item belongs to one order
    left_source: order_items
    right_source: orders
    join_type: many_to_one
    condition: "order_items.order_id = orders.order_id"

  - name: order_item_to_product
    description: Each line item references one product
    left_source: order_items
    right_source: products
    join_type: many_to_one
    condition: "order_items.product_id = products.product_id"'''

    yaml_dimensions = '''dimensions:
  - name: order_date
    description: Date the order was placed
    source: orders
    expression: order_date
    type: date

  - name: region
    description: Geographic region of the customer
    source: customers
    expression: region
    type: string

  - name: customer_segment
    description: "Business segment (Enterprise, Mid-Market, SMB)"
    source: customers
    expression: customer_segment
    type: string
    allowed_values: [Enterprise, Mid-Market, SMB]

  - name: product_category
    description: Top-level product category
    source: products
    expression: category
    type: string'''

    yaml_metrics = '''metrics:
  - name: total_revenue
    description: >
      Total revenue from completed orders. This is the single source
      of truth for revenue across all BI tools and AI agents.
    expression: "SUM(orders.total_amount)"
    type: aggregate
    agg_function: sum
    source: orders
    filters:
      - "orders.order_status = \'completed\'"
    tags: [finance, kpi]

  - name: average_order_value
    description: >
      Average revenue per completed order (total_revenue / order_count).
    expression: "SUM(orders.total_amount) / NULLIF(COUNT(DISTINCT orders.order_id), 0)"
    type: derived
    depends_on: [total_revenue, order_count]
    tags: [finance, kpi]

  - name: active_customers
    description: >
      Count of unique customers who placed at least one order in the period.
    expression: "COUNT(DISTINCT orders.customer_id)"
    type: aggregate
    agg_function: count_distinct
    source: orders
    tags: [customer, kpi]'''

    yaml_full = f'''ossie_version: "0.1"

model:
  name: ecommerce_analytics
  description: >
    E-commerce analytics semantic model defining consistent 
    business metrics across all consuming tools.
  owner: data-platform-team
  tags: [ecommerce, analytics, revenue]

{yaml_sources}

{yaml_relationships}

{yaml_dimensions}

{yaml_metrics}'''

    yaml_map = {
        "Full Model": yaml_full,
        "Sources": yaml_sources,
        "Relationships": yaml_relationships,
        "Dimensions": yaml_dimensions,
        "Metrics": yaml_metrics,
    }
    
    st.code(yaml_map[section], language="yaml")
    
    if section == "Sources":
        st.info("**Sources** name the physical tables behind the model, including database, schema, and primary key. In a Snowflake semantic view that is a logical table in the `TABLES` clause: an alias, a base table, and a `PRIMARY KEY`.")
    elif section == "Relationships":
        st.info("**Relationships** specify join paths between sources, including cardinality. These ensure any consumer can navigate the model correctly — no more accidental fan-out joins.")
    elif section == "Dimensions":
        st.info("**Dimensions** are the attributes used to slice and filter metrics. They can include computed expressions (e.g., `DATE_TRUNC`) and validation rules (`allowed_values`).")
    elif section == "Metrics":
        st.info("**Metrics** are the heart of Ossie — unambiguous business measures with explicit aggregation logic, filters, and dependencies. When every tool reads from this spec, 'Revenue' means the same thing everywhere.")

# =============================================================================
# TAB 3: OSSIE → SNOWFLAKE MAPPING
# =============================================================================
with tab3:
    st.header("How Ossie Maps to Snowflake Semantic Views")
    st.markdown("""
    Snowflake's **Semantic Views** are a native implementation that aligns with Ossie's vision. 
    The mapping is nearly 1:1 — an Ossie YAML can be converted to a Snowflake Semantic View 
    (and vice versa) with minimal transformation.
    """)
    
    st.subheader("Concept Mapping")
    
    mapping_data = [
        {"Ossie Concept": "sources", "Snowflake Equivalent": "TABLES (alias AS base_table)", "Purpose": "Physical table references"},
        {"Ossie Concept": "relationships", "Snowflake Equivalent": "RELATIONSHIPS (... REFERENCES ...)", "Purpose": "Join paths between tables"},
        {"Ossie Concept": "dimensions", "Snowflake Equivalent": "DIMENSIONS (table.dimension AS expr)", "Purpose": "Filterable and groupable attributes"},
        {"Ossie Concept": "metrics", "Snowflake Equivalent": "METRICS (table.metric AS aggregate)", "Purpose": "Aggregated business measures"},
        {"Ossie Concept": "description", "Snowflake Equivalent": "COMMENT = '...'", "Purpose": "Business context and documentation"},
        {"Ossie Concept": "primary_key", "Snowflake Equivalent": "PRIMARY KEY (col)", "Purpose": "Entity identity"},
        {"Ossie Concept": "join_type: many_to_one", "Snowflake Equivalent": "Inferred from PRIMARY KEY", "Purpose": "Cardinality of the relationship"},
        {"Ossie Concept": "filters", "Snowflake Equivalent": "Predicate inside the metric expression", "Purpose": "The business rule travels with the metric"},
    ]
    import pandas as pd
    st.dataframe(pd.DataFrame(mapping_data), use_container_width=True)
    
    st.divider()
    st.subheader("Side-by-Side: Ossie YAML vs Snowflake SQL")
    
    col_ossie, col_sf = st.columns(2)
    
    with col_ossie:
        st.markdown("#### Ossie YAML")
        st.code('''metrics:
  - name: total_revenue
    description: >
      Total revenue from completed orders.
      Single source of truth for all tools.
    expression: "SUM(orders.total_amount)"
    type: aggregate
    source: orders
    filters:
      - "order_status = 'completed'"
    tags: [finance, kpi]''', language="yaml")
    
    with col_sf:
        st.markdown("#### Snowflake Semantic View")
        st.code('''METRICS (
  orders.total_revenue AS SUM(
    IFF(
      orders.order_status = 'completed',
      orders.total_amount,
      NULL
    )
  )
  COMMENT = 'Sum of total_amount for
    completed orders.'
)''', language="sql")
    
    st.divider()
    
    col_ossie2, col_sf2 = st.columns(2)
    with col_ossie2:
        st.markdown("#### Ossie YAML")
        st.code('''relationships:
  - name: order_to_customer
    left_source: orders
    right_source: customers
    join_type: many_to_one
    condition: >
      orders.customer_id = 
      customers.customer_id''', language="yaml")
    
    with col_sf2:
        st.markdown("#### Snowflake Semantic View")
        st.code('''RELATIONSHIPS (
  order_to_customer AS
    orders (customer_id)
      REFERENCES customers (customer_id)
)''', language="sql")
        st.caption("Many orders belong to one customer because `customer_id` is the primary key of `customers`. Snowflake infers that cardinality from the key.")
    
    st.divider()
    st.subheader("Reference Implementations (Converters)")
    st.markdown("""
    The Ossie community has already built converters to translate between Ossie and platform-native formats:
    
    | Converter | Direction | Status |
    |-----------|-----------|--------|
    | **Ossie → Snowflake Semantic Model** | Ossie YAML → Snowflake | Available |
    | **Ossie → dbt MetricFlow** | Ossie YAML → dbt metrics | Available |
    | **Apache Polaris → Ossie** | Polaris catalog → Ossie YAML | Available |
    | **Snowflake → Ossie** | Snowflake Semantic View → Ossie YAML | Planned |
    
    This means you can define metrics **once** in Ossie format and deploy to multiple platforms.
    """)

# =============================================================================
# TAB 4: WITH VS WITHOUT A SEMANTIC VIEW
# =============================================================================
with tab4:
    import pandas as pd

    st.header("Same question, two answers")
    st.markdown("""
    The left query reads the base tables and invents the metric. The right query
    asks the semantic view for the metric by name. The chart is the difference.
    """)

    semantic_view = "OSSIE_DEMO.ECOMMERCE.ecommerce_semantic_model"
    scenarios = {
        "Total Revenue by Region": {
            "dimension": "REGION",
            "metric": "TOTAL_REVENUE",
            "chart": "bar",
            "sort": "without",
            "show_total": True,
            "metric_name": "TOTAL_REVENUE",
            "without_note": "The column is named total_amount, so this query sums every order. Shipped and processing orders are included.",
            "with_note": "The query names total_revenue. The expression under it is what the view applies.",
            "without_sql": """
                SELECT c.region AS region,
                       SUM(o.total_amount) AS total_revenue
                FROM OSSIE_DEMO.ECOMMERCE.orders o
                JOIN OSSIE_DEMO.ECOMMERCE.customers c
                  ON o.customer_id = c.customer_id
                GROUP BY c.region
                ORDER BY total_revenue DESC
            """,
            "with_sql": f"""
                SELECT *
                FROM SEMANTIC_VIEW(
                    {semantic_view}
                    DIMENSIONS customers.region
                    METRICS orders.total_revenue
                )
                ORDER BY total_revenue DESC
            """,
        },
        "Average Order Value by Segment": {
            "dimension": "CUSTOMER_SEGMENT",
            "metric": "AVERAGE_ORDER_VALUE",
            "chart": "bar",
            "sort": "without",
            "show_total": False,
            "metric_name": "AVERAGE_ORDER_VALUE",
            "without_note": "Average order value is recalculated from every order in the segment, including orders that are not completed.",
            "with_note": "The query names average_order_value. That metric is built from completed revenue and the completed order count.",
            "without_sql": """
                SELECT c.customer_segment AS customer_segment,
                       SUM(o.total_amount)
                         / NULLIF(COUNT(DISTINCT o.order_id), 0) AS average_order_value
                FROM OSSIE_DEMO.ECOMMERCE.orders o
                JOIN OSSIE_DEMO.ECOMMERCE.customers c
                  ON o.customer_id = c.customer_id
                GROUP BY c.customer_segment
                ORDER BY average_order_value DESC
            """,
            "with_sql": f"""
                SELECT *
                FROM SEMANTIC_VIEW(
                    {semantic_view}
                    DIMENSIONS customers.customer_segment
                    METRICS orders.average_order_value
                )
                ORDER BY average_order_value DESC
            """,
        },
        "Active Customers Over Time": {
            "dimension": "ORDER_MONTH",
            "metric": "ACTIVE_CUSTOMERS",
            "chart": "line",
            "sort": "dimension",
            "show_total": False,
            "metric_name": "ACTIVE_CUSTOMERS",
            "without_note": "The completed-order rule is copied onto active customers. Months that only have shipped or processing orders drop out.",
            "with_note": "The query names active_customers. Its expression keeps a wider set of statuses than revenue.",
            "without_sql": """
                SELECT DATE_TRUNC('month', o.order_date) AS order_month,
                       COUNT(DISTINCT o.customer_id) AS active_customers
                FROM OSSIE_DEMO.ECOMMERCE.orders o
                WHERE o.order_status = 'completed'
                GROUP BY order_month
                ORDER BY order_month
            """,
            "with_sql": f"""
                SELECT *
                FROM SEMANTIC_VIEW(
                    {semantic_view}
                    DIMENSIONS orders.order_month
                    METRICS orders.active_customers
                )
                ORDER BY order_month
            """,
        },
        "Revenue by Product Category": {
            "dimension": "PRODUCT_CATEGORY",
            "metric": "LINE_REVENUE",
            "chart": "bar",
            "sort": "without",
            "show_total": True,
            "metric_name": "LINE_REVENUE",
            "without_note": "This joins line items and then sums orders.total_amount. A multi-line order is counted once for every line.",
            "with_note": "The query names line_revenue. Its expression sums line totals and does not test order status.",
            "without_sql": """
                SELECT p.category AS product_category,
                       SUM(o.total_amount) AS line_revenue
                FROM OSSIE_DEMO.ECOMMERCE.order_items oi
                JOIN OSSIE_DEMO.ECOMMERCE.products p
                  ON oi.product_id = p.product_id
                JOIN OSSIE_DEMO.ECOMMERCE.orders o
                  ON oi.order_id = o.order_id
                GROUP BY p.category
                ORDER BY line_revenue DESC
            """,
            "with_sql": f"""
                SELECT *
                FROM SEMANTIC_VIEW(
                    {semantic_view}
                    DIMENSIONS products.product_category
                    METRICS order_items.line_revenue
                )
                ORDER BY line_revenue DESC
            """,
        },
        "Monthly Revenue Trend": {
            "dimension": "ORDER_MONTH",
            "metric": "TOTAL_REVENUE",
            "chart": "line",
            "sort": "dimension",
            "show_total": True,
            "metric_name": "TOTAL_REVENUE",
            "without_note": "Revenue is the sum of total_amount for every row. February and March include orders that are not completed.",
            "with_note": "The query names total_revenue. The expression under it keeps completed orders only.",
            "without_sql": """
                SELECT DATE_TRUNC('month', o.order_date) AS order_month,
                       SUM(o.total_amount) AS total_revenue
                FROM OSSIE_DEMO.ECOMMERCE.orders o
                GROUP BY order_month
                ORDER BY order_month
            """,
            "with_sql": f"""
                SELECT *
                FROM SEMANTIC_VIEW(
                    {semantic_view}
                    DIMENSIONS orders.order_month
                    METRICS orders.total_revenue
                )
                ORDER BY order_month
            """,
        },
    }

    order_previews = {
        "TOTAL_REVENUE": """
            SELECT order_id,
                   order_date,
                   order_status,
                   total_amount,
                   IFF(order_status = 'completed', total_amount, NULL) AS counted_amount
            FROM OSSIE_DEMO.ECOMMERCE.orders
            ORDER BY order_date, order_id
        """,
        "AVERAGE_ORDER_VALUE": """
            SELECT order_id,
                   order_date,
                   order_status,
                   total_amount,
                   IFF(order_status = 'completed', order_id, NULL) AS counted_order
            FROM OSSIE_DEMO.ECOMMERCE.orders
            ORDER BY order_date, order_id
        """,
        "ACTIVE_CUSTOMERS": """
            SELECT order_id,
                   order_date,
                   order_status,
                   customer_id,
                   IFF(
                       order_status IN ('completed', 'shipped', 'processing'),
                       customer_id,
                       NULL
                   ) AS counted_customer
            FROM OSSIE_DEMO.ECOMMERCE.orders
            ORDER BY order_date, order_id
        """,
        "LINE_REVENUE": """
            SELECT oi.order_item_id,
                   o.order_id,
                   o.order_status,
                   p.category,
                   oi.line_total AS counted_amount
            FROM OSSIE_DEMO.ECOMMERCE.order_items oi
            JOIN OSSIE_DEMO.ECOMMERCE.orders o
              ON oi.order_id = o.order_id
            JOIN OSSIE_DEMO.ECOMMERCE.products p
              ON oi.product_id = p.product_id
            ORDER BY o.order_date, oi.order_item_id
        """,
    }

    query_choice = st.selectbox("Select a question:", list(scenarios))
    scenario = scenarios[query_choice]

    def run_query(sql):
        frame = session.sql(sql).to_pandas()
        frame.columns = [column.upper() for column in frame.columns]
        return frame

    def metric_expressions(metric_name):
        definition = run_query("""
            SELECT name, expression
            FROM OSSIE_DEMO.INFORMATION_SCHEMA.SEMANTIC_METRICS
            WHERE semantic_view_name = 'ECOMMERCE_SEMANTIC_MODEL'
        """)
        if definition.empty:
            return None, []
        by_name = {
            row["NAME"]: row["EXPRESSION"]
            for _, row in definition.iterrows()
        }
        expression = by_name.get(metric_name)
        if expression is None:
            return None, []
        expression_text = expression.lower()
        related = [
            (name, related_expression)
            for name, related_expression in by_name.items()
            if name != metric_name and name.lower() in expression_text
        ]
        return expression, related

    def selection_caption(expression):
        text = expression.lower()
        if "order_status" not in text:
            return "This expression does not test order status, so every row at this grain is included."
        if "shipped" in text or "processing" in text:
            return "This expression selects completed, shipped, and processing orders."
        if "completed" in text:
            return "This expression selects completed orders. Any other status becomes NULL and drops out of the aggregate."
        return "This is the expression the semantic view applies."

    without_col, with_col = st.columns(2)
    with without_col:
        st.subheader("Without a semantic view")
        st.caption(scenario["without_note"])
        st.code(scenario["without_sql"].strip(), language="sql")
    with with_col:
        st.subheader("With the semantic view")
        st.caption(scenario["with_note"])
        st.markdown("**Generated query**")
        st.code(scenario["with_sql"].strip(), language="sql")
        try:
            expression, related_expressions = metric_expressions(scenario["metric_name"])
        except Exception as error:
            expression, related_expressions = None, []
            st.caption(f"The metric expression could not be read from the semantic view. {error}")
        if expression:
            st.markdown("**Expression the view applies**")
            st.code(expression.strip(), language="sql")
            if related_expressions:
                st.caption("This metric uses the expressions below, and those expressions select the rows.")
                for related_name, related_expression in related_expressions:
                    st.markdown(f"**{related_name.lower()}**")
                    st.code(related_expression.strip(), language="sql")
                    st.caption(selection_caption(related_expression))
            else:
                st.caption(selection_caption(expression))

    preview_sql = order_previews.get(scenario["metric_name"])
    if preview_sql:
        st.markdown("**Rows this metric selects**")
        try:
            selected_rows = run_query(preview_sql)
            counted_column = next(
                column for column in selected_rows.columns if column.startswith("COUNTED")
            )
            counted = int(selected_rows[counted_column].notna().sum())
            left_out = int(selected_rows[counted_column].isna().sum())
            st.caption(f"{counted} rows are selected. {left_out} rows are left out.")
            st.dataframe(selected_rows, use_container_width=True)
        except Exception as error:
            st.caption(f"The selected rows could not be listed. {error}")

    try:
        without_df = run_query(scenario["without_sql"])
        with_df = run_query(scenario["with_sql"])
    except Exception as error:
        st.warning(
            "Run `01_setup.sql` and `02_semantic_view.sql` first so both queries can run. "
            f"Error: {error}"
        )
    else:
        dimension = scenario["dimension"]
        metric = scenario["metric"]
        missing = [
            name
            for name, frame in (("without", without_df), ("with", with_df))
            if dimension not in frame.columns or metric not in frame.columns
        ]
        if missing:
            st.warning(
                f"Expected columns {dimension} and {metric}. "
                f"Without columns: {list(without_df.columns)}. "
                f"With columns: {list(with_df.columns)}."
            )
        else:
            without_values = without_df[[dimension, metric]].copy()
            with_values = with_df[[dimension, metric]].copy()
            without_values[metric] = without_values[metric].astype(float)
            with_values[metric] = with_values[metric].astype(float)

            compared = without_values.merge(
                with_values,
                on=dimension,
                how="outer",
                suffixes=("_WITHOUT", "_WITH"),
            )
            compared["WITHOUT"] = compared[f"{metric}_WITHOUT"]
            compared["WITH"] = compared[f"{metric}_WITH"]
            if scenario["sort"] == "dimension":
                compared = compared.sort_values(dimension)
            else:
                compared = compared.sort_values("WITHOUT", ascending=False, na_position="last")

            if scenario["show_total"]:
                without_total = float(compared["WITHOUT"].fillna(0).sum())
                with_total = float(compared["WITH"].fillna(0).sum())
                total_col, semantic_col, gap_col = st.columns(3)
                total_col.metric("Without a semantic view", f"{without_total:,.0f}")
                semantic_col.metric("With the semantic view", f"{with_total:,.0f}")
                gap_col.metric("Difference", f"{without_total - with_total:,.0f}")

            plot = compared[[dimension, "WITHOUT", "WITH"]].copy()
            plot["Without semantic view"] = plot["WITHOUT"].fillna(0)
            plot["With semantic view"] = plot["WITH"].fillna(0)
            chart_columns = ["Without semantic view", "With semantic view"]
            if scenario["chart"] == "line":
                st.line_chart(plot, x=dimension, y=chart_columns)
            else:
                st.bar_chart(plot, x=dimension, y=chart_columns)

            display = pd.DataFrame({
                dimension.replace("_", " ").title(): compared[dimension],
                "Without semantic view": compared["WITHOUT"],
                "With semantic view": compared["WITH"],
                "Difference": compared["WITHOUT"].fillna(0) - compared["WITH"].fillna(0),
            })
            st.dataframe(display, use_container_width=True)

# =============================================================================
# TAB 5: THE INTEROPERABILITY VISION
# =============================================================================
with tab5:
    st.header("The Interoperability Vision")
    
    st.markdown("""
    ### Before Ossie: Fragmented Semantic Definitions
    """)
    
    st.code("""
    ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ BI Tool  │   │ AI Agent │   │  dbt     │   │ CRM      │
    │          │   │          │   │          │   │          │
    │ Revenue= │   │ Revenue= │   │ Revenue= │   │ Revenue= │
    │ SUM(amt) │   │ SUM(sales│   │ SUM(amt) │   │ SUM(     │
    │          │   │ -returns)│   │ WHERE    │   │  closed_ │
    │          │   │          │   │ status=  │   │  deals)  │
    │          │   │          │   │ 'done'   │   │          │
    └──────────┘   └──────────┘   └──────────┘   └──────────┘
         ↓              ↓              ↓              ↓
    4 different definitions of "Revenue" = CHAOS
    """, language="text")
    
    st.markdown("""
    ### After Ossie: One Definition, Many Consumers
    """)
    
    st.code("""
                    ┌─────────────────────────┐
                    │    Apache Ossie YAML     │
                    │                         │
                    │  total_revenue:          │
                    │    SUM(total_amount)     │
                    │    WHERE status =        │
                    │      'completed'         │
                    │                         │
                    │  🦘 One pouch,           │
                    │     many destinations    │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  Snowflake   │  │  BI Tools    │  │  AI Agents   │
    │  Semantic    │  │  (Tableau,   │  │  (Cortex,    │
    │  Views       │  │   Looker,    │  │   GPT,       │
    │              │  │   Power BI)  │  │   Claude)    │
    └──────────────┘  └──────────────┘  └──────────────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 │
                    Same answer everywhere ✓
    """, language="text")
    
    st.divider()
    
    st.subheader("Why Apache Software Foundation?")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Vendor Neutrality**
        - No single company controls the spec
        - Committership earned through contribution
        - Public mailing lists and GitHub development
        - Formal vote process for spec changes
        """)
    with col2:
        st.markdown("""
        **Enterprise Confidence**
        - ASF governance is proven (Spark, Kafka, Iceberg...)
        - IP protection via Apache License 2.0
        - Long-term sustainability
        - Cross-industry adoption
        """)
    
    st.divider()
    
    st.subheader("What's on the Roadmap?")
    roadmap_items = [
        ("Deeper spec expressiveness", "Advanced metric logic, windowing functions, complex relationships"),
        ("More platform converters", "Adopt Ossie without ripping out existing tools"),
        ("Standardized semantic query spec", "A universal query language any engine can support"),
        ("Apache Polaris integration", "Semantic models discoverable directly from the catalog"),
    ]
    for title, desc in roadmap_items:
        st.markdown(f"**{title}** — {desc}")
    
    st.divider()
    
    st.subheader("Get Involved")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("""
        **Website**  
        [ossie.apache.org](https://ossie.apache.org)
        """)
    with col_b:
        st.markdown("""
        **Slack**  
        [apache-ossie.slack.com](https://join.slack.com/t/apache-ossie/shared_invite/zt-42i1xkgy8-7YQtKEDq7v~mceFmdiLhkA)
        """)
    with col_c:
        st.markdown("""
        **Blog Post**  
        [Snowflake Announcement](https://www.snowflake.com/en/blog/apache-ossie-open-semantic-interchange-incubator/)
        """)

# =============================================================================
# FOOTER
# =============================================================================
st.divider()
st.caption("Built with Streamlit in Snowflake | Apache Ossie is currently undergoing incubation at The Apache Software Foundation.")
