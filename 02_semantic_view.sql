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
=============================================================================*/

USE DATABASE OSSIE_DEMO;
USE SCHEMA ECOMMERCE;

CREATE OR REPLACE SEMANTIC VIEW ecommerce_semantic_model
  COMMENT = 'Snowflake Semantic View aligned with Apache Ossie spec — single source of truth for e-commerce metrics'
AS
-- =========================================================================
-- TABLES (equivalent to Ossie "sources")
-- =========================================================================
DEFINE TABLE orders_t
  BASE_TABLE = 'OSSIE_DEMO.ECOMMERCE.ORDERS'
  PRIMARY_KEY = (order_id)
  COMMENT = 'Completed and in-progress customer orders'
  
  -- Dimensions (equivalent to Ossie "dimensions" on this source)
  DIMENSION order_id
    COMMENT = 'Unique order identifier'
  DIMENSION order_date
    COMMENT = 'Date the order was placed'
  DIMENSION order_month
    EXPRESSION = DATE_TRUNC('month', order_date)
    COMMENT = 'Month the order was placed (truncated)'
  DIMENSION order_status
    COMMENT = 'Current fulfillment status (completed, shipped, processing, cancelled)'
  DIMENSION shipping_method
    COMMENT = 'Shipping method selected by customer'
  DIMENSION customer_id
    COMMENT = 'Foreign key to customers table'
    
  -- Metrics (equivalent to Ossie "metrics")
  METRIC total_revenue
    EXPRESSION = SUM(total_amount)
    COMMENT = 'Total revenue from orders — the single source of truth for revenue across all tools'
  METRIC gross_revenue
    EXPRESSION = SUM(total_amount + discount_amount)
    COMMENT = 'Total order value before discounts'
  METRIC total_discount
    EXPRESSION = SUM(discount_amount)
    COMMENT = 'Total discounts given'
  METRIC order_count
    EXPRESSION = COUNT(DISTINCT order_id)
    COMMENT = 'Number of orders placed'
  METRIC average_order_value
    EXPRESSION = SUM(total_amount) / NULLIF(COUNT(DISTINCT order_id), 0)
    COMMENT = 'Average revenue per order (AOV)'
  METRIC active_customers
    EXPRESSION = COUNT(DISTINCT customer_id)
    COMMENT = 'Unique customers who placed orders in the period'

DEFINE TABLE customers_t
  BASE_TABLE = 'OSSIE_DEMO.ECOMMERCE.CUSTOMERS'
  PRIMARY_KEY = (customer_id)
  COMMENT = 'Registered customers with segmentation data'
  
  DIMENSION customer_id
    COMMENT = 'Unique customer identifier'
  DIMENSION customer_name
    COMMENT = 'Full name of the customer'
  DIMENSION region
    COMMENT = 'Geographic region'
  DIMENSION country
    COMMENT = 'Country of the customer'
  DIMENSION customer_segment
    COMMENT = 'Business segment: Enterprise, Mid-Market, or SMB'
  DIMENSION signup_date
    COMMENT = 'Date the customer registered'

DEFINE TABLE products_t
  BASE_TABLE = 'OSSIE_DEMO.ECOMMERCE.PRODUCTS'
  PRIMARY_KEY = (product_id)
  COMMENT = 'Product catalog with pricing'
  
  DIMENSION product_id
    COMMENT = 'Unique product identifier'
  DIMENSION product_name
    COMMENT = 'Name of the product'
  DIMENSION category AS product_category
    COMMENT = 'Top-level product category'
  DIMENSION subcategory AS product_subcategory
    COMMENT = 'Detailed product subcategory'
  DIMENSION unit_price
    COMMENT = 'List price per unit'

DEFINE TABLE order_items_t
  BASE_TABLE = 'OSSIE_DEMO.ECOMMERCE.ORDER_ITEMS'
  PRIMARY_KEY = (order_item_id)
  COMMENT = 'Line items within each order'
  
  DIMENSION order_item_id
    COMMENT = 'Unique line item identifier'
  DIMENSION order_id
    COMMENT = 'Foreign key to orders'
  DIMENSION product_id
    COMMENT = 'Foreign key to products'
  DIMENSION quantity
    COMMENT = 'Number of units ordered'
    
  METRIC items_sold
    EXPRESSION = SUM(quantity)
    COMMENT = 'Total quantity of items sold'
  METRIC line_revenue
    EXPRESSION = SUM(line_total)
    COMMENT = 'Total revenue from line items'

-- =========================================================================
-- RELATIONSHIPS (equivalent to Ossie "relationships")
-- =========================================================================
DEFINE RELATIONSHIP order_to_customer
  orders_t(customer_id) REFERENCES customers_t(customer_id)
  RELATIONSHIP_TYPE = 'many_to_one'
  COMMENT = 'Each order belongs to one customer'

DEFINE RELATIONSHIP order_item_to_order
  order_items_t(order_id) REFERENCES orders_t(order_id)
  RELATIONSHIP_TYPE = 'many_to_one'
  COMMENT = 'Each line item belongs to one order'

DEFINE RELATIONSHIP order_item_to_product
  order_items_t(product_id) REFERENCES products_t(product_id)
  RELATIONSHIP_TYPE = 'many_to_one'
  COMMENT = 'Each line item references one product'
;

-- Verify the semantic view was created
DESCRIBE SEMANTIC VIEW ecommerce_semantic_model;
