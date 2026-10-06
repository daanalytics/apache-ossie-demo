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
    "Live Query Demo",
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
        st.info("**Sources** define the physical tables backing the model — including database, schema, and primary keys. Equivalent to Snowflake Semantic View `DEFINE TABLE` statements.")
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
        {"Ossie Concept": "sources", "Snowflake Equivalent": "DEFINE TABLE ... BASE_TABLE", "Purpose": "Physical table references"},
        {"Ossie Concept": "relationships", "Snowflake Equivalent": "DEFINE RELATIONSHIP ... REFERENCES", "Purpose": "Join paths between tables"},
        {"Ossie Concept": "dimensions", "Snowflake Equivalent": "DIMENSION column_name", "Purpose": "Filterable/groupable attributes"},
        {"Ossie Concept": "metrics", "Snowflake Equivalent": "METRIC metric_name EXPRESSION = ...", "Purpose": "Aggregated business measures"},
        {"Ossie Concept": "description", "Snowflake Equivalent": "COMMENT = '...'", "Purpose": "Business context and documentation"},
        {"Ossie Concept": "primary_key", "Snowflake Equivalent": "PRIMARY_KEY = (col)", "Purpose": "Entity identity"},
        {"Ossie Concept": "join_type: many_to_one", "Snowflake Equivalent": "RELATIONSHIP_TYPE = 'many_to_one'", "Purpose": "Cardinality specification"},
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
        st.code('''DEFINE TABLE orders_t
  BASE_TABLE = 'OSSIE_DEMO.ECOMMERCE.ORDERS'
  
  METRIC total_revenue
    EXPRESSION = SUM(total_amount)
    COMMENT = 'Total revenue from completed 
    orders. Single source of truth for 
    all tools.'
    ''', language="sql")
    
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
        st.code('''DEFINE RELATIONSHIP order_to_customer
  orders_t(customer_id) 
    REFERENCES customers_t(customer_id)
  RELATIONSHIP_TYPE = 'many_to_one'
  COMMENT = 'Each order belongs to 
  one customer\'''', language="sql")
    
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
# TAB 4: LIVE QUERY DEMO
# =============================================================================
with tab4:
    st.header("Live Query Demo")
    st.markdown("""
    These queries demonstrate how the semantic model provides **consistent metric definitions** 
    that any tool or AI agent can rely on. The metrics below match exactly what's defined 
    in both the Ossie YAML and the Snowflake Semantic View.
    """)
    
    query_choice = st.selectbox(
        "Select a metric to explore:",
        [
            "Total Revenue by Region",
            "Average Order Value by Segment",
            "Active Customers Over Time",
            "Revenue by Product Category",
            "Monthly Revenue Trend",
        ]
    )
    
    queries = {
        "Total Revenue by Region": """
            SELECT c.region, 
                   SUM(o.total_amount) AS total_revenue,
                   COUNT(DISTINCT o.order_id) AS order_count
            FROM OSSIE_DEMO.ECOMMERCE.orders o
            JOIN OSSIE_DEMO.ECOMMERCE.customers c 
              ON o.customer_id = c.customer_id
            WHERE o.order_status = 'completed'
            GROUP BY c.region
            ORDER BY total_revenue DESC
        """,
        "Average Order Value by Segment": """
            SELECT c.customer_segment,
                   SUM(o.total_amount) / NULLIF(COUNT(DISTINCT o.order_id), 0) AS average_order_value,
                   COUNT(DISTINCT o.order_id) AS order_count,
                   COUNT(DISTINCT o.customer_id) AS active_customers
            FROM OSSIE_DEMO.ECOMMERCE.orders o
            JOIN OSSIE_DEMO.ECOMMERCE.customers c 
              ON o.customer_id = c.customer_id
            WHERE o.order_status = 'completed'
            GROUP BY c.customer_segment
            ORDER BY average_order_value DESC
        """,
        "Active Customers Over Time": """
            SELECT DATE_TRUNC('month', o.order_date) AS order_month,
                   COUNT(DISTINCT o.customer_id) AS active_customers,
                   SUM(o.total_amount) AS total_revenue
            FROM OSSIE_DEMO.ECOMMERCE.orders o
            WHERE o.order_status IN ('completed', 'shipped', 'processing')
            GROUP BY order_month
            ORDER BY order_month
        """,
        "Revenue by Product Category": """
            SELECT p.category AS product_category,
                   SUM(oi.line_total) AS revenue,
                   SUM(oi.quantity) AS items_sold,
                   SUM(oi.line_total) / NULLIF(SUM(oi.quantity), 0) AS avg_item_price
            FROM OSSIE_DEMO.ECOMMERCE.order_items oi
            JOIN OSSIE_DEMO.ECOMMERCE.products p 
              ON oi.product_id = p.product_id
            JOIN OSSIE_DEMO.ECOMMERCE.orders o 
              ON oi.order_id = o.order_id
            WHERE o.order_status = 'completed'
            GROUP BY p.category
            ORDER BY revenue DESC
        """,
        "Monthly Revenue Trend": """
            SELECT DATE_TRUNC('month', o.order_date) AS order_month,
                   SUM(o.total_amount) AS total_revenue,
                   SUM(o.discount_amount) AS total_discount,
                   SUM(o.total_amount) / NULLIF(COUNT(DISTINCT o.order_id), 0) AS aov
            FROM OSSIE_DEMO.ECOMMERCE.orders o
            WHERE o.order_status = 'completed'
            GROUP BY order_month
            ORDER BY order_month
        """,
    }
    
    with st.expander("View SQL (derived from semantic model definition)", expanded=False):
        st.code(queries[query_choice], language="sql")
        st.caption("This query implements the metric exactly as defined in the Ossie YAML — same filters, same aggregation logic.")
    
    try:
        df = session.sql(queries[query_choice]).to_pandas()
        
        if query_choice == "Total Revenue by Region":
            col_chart, col_table = st.columns([2, 1])
            with col_chart:
                st.bar_chart(df, x="REGION", y="TOTAL_REVENUE")
            with col_table:
                st.dataframe(df)
                
        elif query_choice == "Average Order Value by Segment":
            col_chart, col_table = st.columns([2, 1])
            with col_chart:
                st.bar_chart(df, x="CUSTOMER_SEGMENT", y="AVERAGE_ORDER_VALUE")
            with col_table:
                st.dataframe(df)
                
        elif query_choice == "Active Customers Over Time":
            st.line_chart(df, x="ORDER_MONTH", y=["ACTIVE_CUSTOMERS"])
            st.dataframe(df)
            
        elif query_choice == "Revenue by Product Category":
            col_chart, col_table = st.columns([2, 1])
            with col_chart:
                st.bar_chart(df, x="PRODUCT_CATEGORY", y="REVENUE")
            with col_table:
                st.dataframe(df)
                
        elif query_choice == "Monthly Revenue Trend":
            st.line_chart(df, x="ORDER_MONTH", y=["TOTAL_REVENUE", "TOTAL_DISCOUNT"])
            st.dataframe(df)
            
    except Exception as e:
        st.warning(f"Run `01_setup.sql` first to create the sample data. Error: {e}")
    
    st.divider()
    st.subheader("Why This Matters")
    st.markdown("""
    Every query above implements a metric **exactly as defined** in the Ossie YAML:
    - `total_revenue` → `SUM(total_amount)` with filter `order_status = 'completed'`  
    - `average_order_value` → `SUM(total_amount) / NULLIF(COUNT(DISTINCT order_id), 0)`  
    - `active_customers` → `COUNT(DISTINCT customer_id)`  
    
    Whether this query comes from a BI dashboard, an AI agent, or a SQL IDE — the 
    result is **identical** because the definition lives in one place.
    """)

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
