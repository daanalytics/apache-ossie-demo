export const YAML_SECTIONS = ["Full Model", "Sources", "Relationships", "Dimensions", "Metrics"] as const;

export type YamlSection = (typeof YAML_SECTIONS)[number];

const yamlSources = `sources:
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
    primary_key: product_id`;

const yamlRelationships = `relationships:
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
    condition: "order_items.product_id = products.product_id"`;

const yamlDimensions = `dimensions:
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
    type: string`;

const yamlMetrics = `metrics:
  - name: total_revenue
    description: >
      Total revenue from completed orders. This is the single source
      of truth for revenue across all BI tools and AI agents.
    expression: "SUM(orders.total_amount)"
    type: aggregate
    agg_function: sum
    source: orders
    filters:
      - "orders.order_status = 'completed'"
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
    tags: [customer, kpi]`;

export const YAML: Record<YamlSection, string> = {
  "Full Model": `ossie_version: "0.1"

model:
  name: ecommerce_analytics
  description: >
    E-commerce analytics semantic model defining consistent
    business metrics across all consuming tools.
  owner: data-platform-team
  tags: [ecommerce, analytics, revenue]

${yamlSources}

${yamlRelationships}

${yamlDimensions}

${yamlMetrics}`,
  Sources: yamlSources,
  Relationships: yamlRelationships,
  Dimensions: yamlDimensions,
  Metrics: yamlMetrics,
};

export const SECTION_NOTES: Partial<Record<YamlSection, string>> = {
  Sources:
    "Sources name the physical tables behind the model, including database, schema, and primary key. In a Snowflake semantic view that is a logical table in the TABLES clause: an alias, a base table, and a PRIMARY KEY.",
  Relationships:
    "Relationships specify join paths between sources, including cardinality. These ensure any consumer can navigate the model correctly — no more accidental fan-out joins.",
  Dimensions:
    "Dimensions are the attributes used to slice and filter metrics. They can include computed expressions (e.g., DATE_TRUNC) and validation rules (allowed_values).",
  Metrics:
    "Metrics are the heart of Ossie — unambiguous business measures with explicit aggregation logic, filters, and dependencies. When every tool reads from this spec, Revenue means the same thing everywhere.",
};

export const MAPPING = [
  ["sources", "TABLES (alias AS base_table)", "Physical table references"],
  ["relationships", "RELATIONSHIPS (... REFERENCES ...)", "Join paths between tables"],
  ["dimensions", "DIMENSIONS (table.dimension AS expr)", "Filterable and groupable attributes"],
  ["metrics", "METRICS (table.metric AS aggregate)", "Aggregated business measures"],
  ["description", "COMMENT = '...'", "Business context and documentation"],
  ["primary_key", "PRIMARY KEY (col)", "Entity identity"],
  ["join_type: many_to_one", "Inferred from PRIMARY KEY", "Cardinality of the relationship"],
  ["filters", "Predicate inside the metric expression", "The business rule travels with the metric"],
];

export const REVENUE_YAML = `metrics:
  - name: total_revenue
    description: >
      Total revenue from completed orders.
      Single source of truth for all tools.
    expression: "SUM(orders.total_amount)"
    type: aggregate
    source: orders
    filters:
      - "order_status = 'completed'"
    tags: [finance, kpi]`;

export const REVENUE_SQL = `METRICS (
  orders.total_revenue AS SUM(
    IFF(
      orders.order_status = 'completed',
      orders.total_amount,
      NULL
    )
  )
  COMMENT = 'Sum of total_amount for
    completed orders.'
)`;

export const RELATIONSHIP_YAML = `relationships:
  - name: order_to_customer
    left_source: orders
    right_source: customers
    join_type: many_to_one
    condition: >
      orders.customer_id =
      customers.customer_id`;

export const RELATIONSHIP_SQL = `RELATIONSHIPS (
  order_to_customer AS
    orders (customer_id)
      REFERENCES customers (customer_id)
)`;

export const BEFORE = `┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ BI Tool  │   │ AI Agent │   │  dbt     │   │ CRM      │
│          │   │          │   │          │   │          │
│ Revenue= │   │ Revenue= │   │ Revenue= │   │ Revenue= │
│ SUM(amt) │   │ SUM(sales│   │ SUM(amt) │   │ SUM(     │
│          │   │ -returns)│   │ WHERE    │   │  closed_ │
│          │   │          │   │ status=  │   │  deals)  │
│          │   │          │   │ 'done'   │   │          │
└──────────┘   └──────────┘   └──────────┘   └──────────┘
     ↓              ↓              ↓              ↓
4 different definitions of "Revenue" = CHAOS`;

export const AFTER = `                ┌─────────────────────────┐
                │    Apache Ossie YAML     │
                │                         │
                │  total_revenue:          │
                │    SUM(total_amount)     │
                │    WHERE status =        │
                │      'completed'         │
                │                         │
                │  One pouch,              │
                │  many destinations       │
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
                Same answer everywhere`;

export const TABS = [
  { id: "about", label: "What is Ossie?" },
  { id: "yaml", label: "Ossie YAML Spec" },
  { id: "mapping", label: "Ossie → Snowflake Mapping" },
  { id: "compare", label: "With vs Without" },
  { id: "vision", label: "The Vision" },
] as const;

export type TabId = (typeof TABS)[number]["id"];

export function tabFrom(value: string | undefined): TabId {
  return TABS.some((tab) => tab.id === value) ? (value as TabId) : "about";
}

export function sectionFrom(value: string | undefined): YamlSection {
  return YAML_SECTIONS.includes(value as YamlSection) ? (value as YamlSection) : "Full Model";
}
