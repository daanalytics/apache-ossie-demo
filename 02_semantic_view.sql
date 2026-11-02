/*=============================================================================
  Apache Ossie + Snowflake Demo — Semantic View
  
  This script creates a Snowflake Semantic View that mirrors the Ossie YAML
  model. It demonstrates the 1:1 conceptual mapping between the open spec
  and Snowflake's native semantic layer.
  
  Ossie Concept         → Snowflake Semantic View Concept
  ─────────────────────────────────────────────────────────
  sources               → tables (with base_table reference)
  relationships         → relationships (join paths)
  dimensions            → dimensions (on each table)
  metrics               → metrics (measures/facts on tables)
  
  Run as ACCOUNTADMIN

=============================================================================*/
USE ROLE ACCOUNTADMIN;

USE DATABASE OSSIE_DEMO;
USE SCHEMA ECOMMERCE;

CREATE OR REPLACE SEMANTIC VIEW ecommerce_semantic_model

  -- =========================================================================
  -- TABLES (equivalent to Ossie "sources")
  -- =========================================================================
  TABLES (
    orders_t AS OSSIE_DEMO.ECOMMERCE.ORDERS
      PRIMARY KEY (order_id)
      COMMENT = 'Completed and in-progress customer orders',

    customers_t AS OSSIE_DEMO.ECOMMERCE.CUSTOMERS
      PRIMARY KEY (customer_id)
      COMMENT = 'Registered customers with segmentation data',

    products_t AS OSSIE_DEMO.ECOMMERCE.PRODUCTS
      PRIMARY KEY (product_id)
      COMMENT = 'Product catalog with pricing',

    order_items_t AS OSSIE_DEMO.ECOMMERCE.ORDER_ITEMS
      PRIMARY KEY (order_item_id)
      COMMENT = 'Line items within each order'
  )

  -- =========================================================================
  -- RELATIONSHIPS (equivalent to Ossie "relationships")
  -- =========================================================================
  RELATIONSHIPS (
    order_to_customer AS
      orders_t(customer_id) REFERENCES customers_t,
    order_item_to_order AS
      order_items_t(order_id) REFERENCES orders_t,
    order_item_to_product AS
      order_items_t(product_id) REFERENCES products_t
  )

  -- =========================================================================
  -- DIMENSIONS (equivalent to Ossie "dimensions")
  -- =========================================================================
  DIMENSIONS (
    -- Orders dimensions
    orders_t.order_id AS order_id
      COMMENT = 'Unique order identifier',
    orders_t.order_date AS order_date
      COMMENT = 'Date the order was placed',
    orders_t.order_month AS DATE_TRUNC('month', order_date)
      COMMENT = 'Month the order was placed (truncated)',
    orders_t.order_status AS order_status
      COMMENT = 'Current fulfillment status (completed, shipped, processing, cancelled)',
    orders_t.shipping_method AS shipping_method
      COMMENT = 'Shipping method selected by customer',
    orders_t.customer_id AS customer_id
      COMMENT = 'Foreign key to customers table',

    -- Customers dimensions
    customers_t.customer_id AS customer_id
      COMMENT = 'Unique customer identifier',
    customers_t.customer_name AS customer_name
      COMMENT = 'Full name of the customer',
    customers_t.region AS region
      COMMENT = 'Geographic region',
    customers_t.country AS country
      COMMENT = 'Country of the customer',
    customers_t.customer_segment AS customer_segment
      COMMENT = 'Business segment: Enterprise, Mid-Market, or SMB',
    customers_t.signup_date AS signup_date
      COMMENT = 'Date the customer registered',

    -- Products dimensions
    products_t.product_id AS product_id
      COMMENT = 'Unique product identifier',
    products_t.product_name AS product_name
      COMMENT = 'Name of the product',
    products_t.product_category AS category
      COMMENT = 'Top-level product category',
    products_t.product_subcategory AS subcategory
      COMMENT = 'Detailed product subcategory',
    products_t.unit_price AS unit_price
      COMMENT = 'List price per unit',

    -- Order items dimensions
    order_items_t.order_item_id AS order_item_id
      COMMENT = 'Unique line item identifier',
    order_items_t.order_id AS order_id
      COMMENT = 'Foreign key to orders',
    order_items_t.product_id AS product_id
      COMMENT = 'Foreign key to products',
    order_items_t.quantity AS quantity
      COMMENT = 'Number of units ordered'
  )

  -- =========================================================================
  -- METRICS (equivalent to Ossie "metrics")
  -- =========================================================================
  METRICS (
    -- Orders metrics
    orders_t.total_revenue AS SUM(total_amount)
      COMMENT = 'Total revenue from orders — the single source of truth for revenue across all tools',
    orders_t.gross_revenue AS SUM(total_amount + discount_amount)
      COMMENT = 'Total order value before discounts',
    orders_t.total_discount AS SUM(discount_amount)
      COMMENT = 'Total discounts given',
    orders_t.order_count AS COUNT(DISTINCT order_id)
      COMMENT = 'Number of orders placed',
    orders_t.average_order_value AS SUM(total_amount) / NULLIF(COUNT(DISTINCT order_id), 0)
      COMMENT = 'Average revenue per order (AOV)',
    orders_t.active_customers AS COUNT(DISTINCT customer_id)
      COMMENT = 'Unique customers who placed orders in the period',

    -- Order items metrics
    order_items_t.items_sold AS SUM(quantity)
      COMMENT = 'Total quantity of items sold',
    order_items_t.line_revenue AS SUM(line_total)
      COMMENT = 'Total revenue from line items'
  )

  COMMENT = 'Snowflake Semantic View aligned with Apache Ossie spec — single source of truth for e-commerce metrics'
;

-- Verify the semantic view was created
DESCRIBE SEMANTIC VIEW ecommerce_semantic_model;
