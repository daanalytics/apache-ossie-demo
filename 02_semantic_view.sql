/*=============================================================================
  Apache Ossie + Snowflake Demo — Semantic View

  Creates a Snowflake semantic view that carries the same context as
  ossie_semantic_model.yaml: tables, relationships, dimensions, and metrics.

  Ossie concept          Snowflake semantic view
  ----------------------------------------------------------------
  sources                TABLES (logical alias AS physical table)
  primary_key            PRIMARY KEY
  relationships          RELATIONSHIPS (... REFERENCES ...)
  join_type              Inferred from the referenced PRIMARY KEY
  dimensions             DIMENSIONS
  metrics                METRICS
  description            COMMENT
  metric filters         Predicates inside the metric expression

  A query-time WHERE clause is optional, so a status rule has to live in
  the expression. Otherwise the next query can skip it.

  Run as ACCOUNTADMIN
=============================================================================*/
USE ROLE ACCOUNTADMIN;

USE DATABASE OSSIE_DEMO;
USE SCHEMA ECOMMERCE;

CREATE OR REPLACE SEMANTIC VIEW ecommerce_semantic_model

  TABLES (
    orders AS OSSIE_DEMO.ECOMMERCE.ORDERS
      PRIMARY KEY (order_id)
      COMMENT = 'Completed and in-progress customer orders',
    customers AS OSSIE_DEMO.ECOMMERCE.CUSTOMERS
      PRIMARY KEY (customer_id)
      COMMENT = 'Registered customers with segmentation data',
    products AS OSSIE_DEMO.ECOMMERCE.PRODUCTS
      PRIMARY KEY (product_id)
      COMMENT = 'Product catalog with pricing',
    order_items AS OSSIE_DEMO.ECOMMERCE.ORDER_ITEMS
      PRIMARY KEY (order_item_id)
      COMMENT = 'Line items within each order'
  )

  -- Cardinality follows the primary key. Many orders reference one customer,
  -- many line items reference one order, and many line items reference one product.
  RELATIONSHIPS (
    order_to_customer AS
      orders (customer_id) REFERENCES customers (customer_id),
    order_item_to_order AS
      order_items (order_id) REFERENCES orders (order_id),
    order_item_to_product AS
      order_items (product_id) REFERENCES products (product_id)
  )

  FACTS (
    products.unit_cost AS cost_price
      COMMENT = 'Product cost price used by gross margin',
    order_items.extended_cost AS quantity * products.unit_cost
      COMMENT = 'Line cost: quantity times product cost price'
  )

  DIMENSIONS (
    orders.order_id AS order_id
      COMMENT = 'Unique order identifier',
    orders.order_date AS order_date
      COMMENT = 'Date the order was placed',
    orders.order_month AS DATE_TRUNC('month', order_date)
      COMMENT = 'Month the order was placed',
    orders.order_status AS order_status
      COMMENT = 'Fulfillment status: completed, shipped, processing, or cancelled',
    orders.shipping_method AS shipping_method
      COMMENT = 'Shipping method selected by the customer',
    orders.customer_id AS customer_id
      COMMENT = 'Customer who placed the order',

    customers.customer_id AS customer_id
      COMMENT = 'Unique customer identifier',
    customers.customer_name AS customer_name
      COMMENT = 'Full name of the customer',
    customers.region AS region
      COMMENT = 'Geographic region of the customer',
    customers.country AS country
      COMMENT = 'Country of the customer',
    customers.customer_segment AS customer_segment
      COMMENT = 'Business segment: Enterprise, Mid-Market, or SMB',
    customers.signup_date AS signup_date
      COMMENT = 'Date the customer registered',

    products.product_id AS product_id
      COMMENT = 'Unique product identifier',
    products.product_name AS product_name
      COMMENT = 'Name of the product',
    products.product_category AS category
      COMMENT = 'Top-level product category',
    products.product_subcategory AS subcategory
      COMMENT = 'Detailed product subcategory',
    products.unit_price AS unit_price
      COMMENT = 'List price per unit',

    order_items.order_item_id AS order_item_id
      COMMENT = 'Unique line item identifier',
    order_items.order_id AS order_id
      COMMENT = 'Order this line item belongs to',
    order_items.product_id AS product_id
      COMMENT = 'Product on this line item',
    order_items.quantity AS quantity
      COMMENT = 'Number of units ordered'
  )

  METRICS (
    orders.total_revenue AS SUM(IFF(orders.order_status = 'completed', orders.total_amount, NULL))
      WITH SYNONYMS = ('revenue')
      COMMENT = 'Sum of total_amount for completed orders. Shipped, processing, and cancelled orders are excluded.',
    orders.gross_revenue AS SUM(IFF(orders.order_status = 'completed', orders.total_amount + orders.discount_amount, NULL))
      COMMENT = 'Completed-order value before discounts (total_amount plus discount_amount).',
    orders.total_discount AS SUM(IFF(orders.order_status = 'completed', orders.discount_amount, NULL))
      COMMENT = 'Discounts on completed orders.',
    orders.order_count AS COUNT(DISTINCT IFF(orders.order_status = 'completed', orders.order_id, NULL))
      COMMENT = 'Number of completed orders.',
    orders.average_order_value AS orders.total_revenue / NULLIF(orders.order_count, 0)
      WITH SYNONYMS = ('aov')
      COMMENT = 'Completed revenue divided by the completed order count.',
    orders.active_customers AS COUNT(DISTINCT IFF(orders.order_status IN ('completed', 'shipped', 'processing'), orders.customer_id, NULL))
      COMMENT = 'Customers with at least one completed, shipped, or processing order.',
    orders.revenue_per_customer AS orders.total_revenue / NULLIF(orders.active_customers, 0)
      COMMENT = 'Completed revenue divided by active customers. Each input keeps its own status rule.',

    order_items.items_sold AS SUM(order_items.quantity)
      COMMENT = 'Total quantity of items sold. The Ossie model applies no order-status filter.',
    order_items.line_revenue AS SUM(order_items.line_total)
      COMMENT = 'Sum of line totals. No order-status filter; category cuts use this metric.',
    order_items.line_cost AS SUM(order_items.extended_cost)
      COMMENT = 'Sum of quantity times product cost.',
    order_items.gross_margin AS (order_items.line_revenue - order_items.line_cost) / NULLIF(order_items.line_revenue, 0)
      COMMENT = 'Gross margin ratio: (line revenue minus line cost) divided by line revenue.'
  )

  COMMENT = 'E-commerce semantic view aligned with the Apache Ossie model. Metric filters are part of the expressions.'
;

DESCRIBE SEMANTIC VIEW ecommerce_semantic_model;
