export type Scenario = {
  question: string;
  dimension: string;
  metric: string;
  chart: "bar" | "line";
  sortByDimension: boolean;
  showTotal: boolean;
  withoutNote: string;
  withNote: string;
  withoutSql: string;
  withSql: string;
  previewSql: string;
};

const VIEW = "OSSIE_DEMO.ECOMMERCE.ecommerce_semantic_model";

export const SCENARIOS: Scenario[] = [
  {
    question: "Total Revenue by Region",
    dimension: "REGION",
    metric: "TOTAL_REVENUE",
    chart: "bar",
    sortByDimension: false,
    showTotal: true,
    withoutNote:
      "The column is named total_amount, so this query sums every order. Shipped and processing orders are included.",
    withNote: "The query names total_revenue. The expression under it is what the view applies.",
    withoutSql: `SELECT c.region AS region,
       SUM(o.total_amount) AS total_revenue
FROM OSSIE_DEMO.ECOMMERCE.orders o
JOIN OSSIE_DEMO.ECOMMERCE.customers c
  ON o.customer_id = c.customer_id
GROUP BY c.region
ORDER BY total_revenue DESC`,
    withSql: `SELECT *
FROM SEMANTIC_VIEW(
    ${VIEW}
    DIMENSIONS customers.region
    METRICS orders.total_revenue
)
ORDER BY total_revenue DESC`,
    previewSql: `SELECT order_id,
       order_date,
       order_status,
       total_amount,
       IFF(order_status = 'completed', total_amount, NULL) AS counted_amount
FROM OSSIE_DEMO.ECOMMERCE.orders
ORDER BY order_date, order_id`,
  },
  {
    question: "Average Order Value by Segment",
    dimension: "CUSTOMER_SEGMENT",
    metric: "AVERAGE_ORDER_VALUE",
    chart: "bar",
    sortByDimension: false,
    showTotal: false,
    withoutNote:
      "Average order value is recalculated from every order in the segment, including orders that are not completed.",
    withNote:
      "The query names average_order_value. That metric is built from completed revenue and the completed order count.",
    withoutSql: `SELECT c.customer_segment AS customer_segment,
       SUM(o.total_amount)
         / NULLIF(COUNT(DISTINCT o.order_id), 0) AS average_order_value
FROM OSSIE_DEMO.ECOMMERCE.orders o
JOIN OSSIE_DEMO.ECOMMERCE.customers c
  ON o.customer_id = c.customer_id
GROUP BY c.customer_segment
ORDER BY average_order_value DESC`,
    withSql: `SELECT *
FROM SEMANTIC_VIEW(
    ${VIEW}
    DIMENSIONS customers.customer_segment
    METRICS orders.average_order_value
)
ORDER BY average_order_value DESC`,
    previewSql: `SELECT order_id,
       order_date,
       order_status,
       total_amount,
       IFF(order_status = 'completed', order_id, NULL) AS counted_order
FROM OSSIE_DEMO.ECOMMERCE.orders
ORDER BY order_date, order_id`,
  },
  {
    question: "Active Customers Over Time",
    dimension: "ORDER_MONTH",
    metric: "ACTIVE_CUSTOMERS",
    chart: "line",
    sortByDimension: true,
    showTotal: false,
    withoutNote:
      "The completed-order rule is copied onto active customers. Months that only have shipped or processing orders drop out.",
    withNote: "The query names active_customers. Its expression keeps a wider set of statuses than revenue.",
    withoutSql: `SELECT DATE_TRUNC('month', o.order_date) AS order_month,
       COUNT(DISTINCT o.customer_id) AS active_customers
FROM OSSIE_DEMO.ECOMMERCE.orders o
WHERE o.order_status = 'completed'
GROUP BY order_month
ORDER BY order_month`,
    withSql: `SELECT *
FROM SEMANTIC_VIEW(
    ${VIEW}
    DIMENSIONS orders.order_month
    METRICS orders.active_customers
)
ORDER BY order_month`,
    previewSql: `SELECT order_id,
       order_date,
       order_status,
       customer_id,
       IFF(
           order_status IN ('completed', 'shipped', 'processing'),
           customer_id,
           NULL
       ) AS counted_customer
FROM OSSIE_DEMO.ECOMMERCE.orders
ORDER BY order_date, order_id`,
  },
  {
    question: "Revenue by Product Category",
    dimension: "PRODUCT_CATEGORY",
    metric: "LINE_REVENUE",
    chart: "bar",
    sortByDimension: false,
    showTotal: true,
    withoutNote:
      "This joins line items and then sums orders.total_amount. A multi-line order is counted once for every line.",
    withNote: "The query names line_revenue. Its expression sums line totals and does not test order status.",
    withoutSql: `SELECT p.category AS product_category,
       SUM(o.total_amount) AS line_revenue
FROM OSSIE_DEMO.ECOMMERCE.order_items oi
JOIN OSSIE_DEMO.ECOMMERCE.products p
  ON oi.product_id = p.product_id
JOIN OSSIE_DEMO.ECOMMERCE.orders o
  ON oi.order_id = o.order_id
GROUP BY p.category
ORDER BY line_revenue DESC`,
    withSql: `SELECT *
FROM SEMANTIC_VIEW(
    ${VIEW}
    DIMENSIONS products.product_category
    METRICS order_items.line_revenue
)
ORDER BY line_revenue DESC`,
    previewSql: `SELECT oi.order_item_id,
       o.order_id,
       o.order_status,
       p.category,
       oi.line_total AS counted_amount
FROM OSSIE_DEMO.ECOMMERCE.order_items oi
JOIN OSSIE_DEMO.ECOMMERCE.orders o
  ON oi.order_id = o.order_id
JOIN OSSIE_DEMO.ECOMMERCE.products p
  ON oi.product_id = p.product_id
ORDER BY o.order_date, oi.order_item_id`,
  },
  {
    question: "Monthly Revenue Trend",
    dimension: "ORDER_MONTH",
    metric: "TOTAL_REVENUE",
    chart: "line",
    sortByDimension: true,
    showTotal: true,
    withoutNote:
      "Revenue is the sum of total_amount for every row. February and March include orders that are not completed.",
    withNote: "The query names total_revenue. The expression under it keeps completed orders only.",
    withoutSql: `SELECT DATE_TRUNC('month', o.order_date) AS order_month,
       SUM(o.total_amount) AS total_revenue
FROM OSSIE_DEMO.ECOMMERCE.orders o
GROUP BY order_month
ORDER BY order_month`,
    withSql: `SELECT *
FROM SEMANTIC_VIEW(
    ${VIEW}
    DIMENSIONS orders.order_month
    METRICS orders.total_revenue
)
ORDER BY order_month`,
    previewSql: `SELECT order_id,
       order_date,
       order_status,
       total_amount,
       IFF(order_status = 'completed', total_amount, NULL) AS counted_amount
FROM OSSIE_DEMO.ECOMMERCE.orders
ORDER BY order_date, order_id`,
  },
];

export function scenarioFor(question: string | undefined): Scenario {
  return SCENARIOS.find((scenario) => scenario.question === question) ?? SCENARIOS[0];
}
