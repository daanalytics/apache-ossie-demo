/*=============================================================================
  Apache Ossie + Snowflake Demo — Setup Script
  
  Creates a sample e-commerce dataset to demonstrate how Apache Ossie's
  vendor-neutral semantic specification maps to Snowflake Semantic Views.
=============================================================================*/

-- 1. Database & Schema
CREATE DATABASE IF NOT EXISTS OSSIE_DEMO;
USE DATABASE OSSIE_DEMO;

CREATE SCHEMA IF NOT EXISTS ECOMMERCE;
USE SCHEMA ECOMMERCE;

-- 2. Tables
CREATE OR REPLACE TABLE customers (
    customer_id     INT,
    customer_name   VARCHAR(100),
    email           VARCHAR(150),
    region          VARCHAR(50),
    country         VARCHAR(50),
    signup_date     DATE,
    customer_segment VARCHAR(30)
);

CREATE OR REPLACE TABLE products (
    product_id      INT,
    product_name    VARCHAR(150),
    category        VARCHAR(50),
    subcategory     VARCHAR(50),
    unit_price      NUMBER(10,2),
    cost_price      NUMBER(10,2)
);

CREATE OR REPLACE TABLE orders (
    order_id        INT,
    customer_id     INT,
    order_date      DATE,
    order_status    VARCHAR(20),
    shipping_method VARCHAR(30),
    total_amount    NUMBER(12,2),
    discount_amount NUMBER(10,2)
);

CREATE OR REPLACE TABLE order_items (
    order_item_id   INT,
    order_id        INT,
    product_id      INT,
    quantity        INT,
    unit_price      NUMBER(10,2),
    line_total      NUMBER(12,2)
);

-- 3. Sample Data — Customers
INSERT INTO customers VALUES
(1,  'Alice Johnson',    'alice@example.com',    'North America', 'United States', '2023-01-15', 'Enterprise'),
(2,  'Bob Smith',        'bob@example.com',      'Europe',        'Germany',       '2023-02-20', 'SMB'),
(3,  'Carlos Rivera',    'carlos@example.com',   'North America', 'Mexico',        '2023-03-10', 'Enterprise'),
(4,  'Diana Chen',       'diana@example.com',    'Asia Pacific',  'Singapore',     '2023-04-05', 'Mid-Market'),
(5,  'Erik Andersson',   'erik@example.com',     'Europe',        'Sweden',        '2023-05-22', 'SMB'),
(6,  'Fatima Al-Hassan', 'fatima@example.com',   'Middle East',   'UAE',           '2023-06-01', 'Enterprise'),
(7,  'George Tanaka',    'george@example.com',   'Asia Pacific',  'Japan',         '2023-07-14', 'Mid-Market'),
(8,  'Hannah Mueller',   'hannah@example.com',   'Europe',        'Germany',       '2023-08-30', 'Enterprise'),
(9,  'Ivan Petrov',      'ivan@example.com',     'Europe',        'Netherlands',   '2023-09-12', 'SMB'),
(10, 'Julia Santos',     'julia@example.com',    'South America', 'Brazil',        '2023-10-25', 'Mid-Market'),
(11, 'Kevin Park',       'kevin@example.com',    'Asia Pacific',  'South Korea',   '2023-11-08', 'Enterprise'),
(12, 'Laura Martinez',   'laura@example.com',    'North America', 'United States', '2023-12-01', 'SMB'),
(13, 'Mohammed Ali',     'mohammed@example.com', 'Middle East',   'Saudi Arabia',  '2024-01-15', 'Enterprise'),
(14, 'Nina Johansson',   'nina@example.com',     'Europe',        'Sweden',        '2024-02-10', 'Mid-Market'),
(15, 'Oscar Reyes',      'oscar@example.com',    'South America', 'Colombia',      '2024-03-05', 'SMB');

-- 4. Sample Data — Products
INSERT INTO products VALUES
(101, 'Cloud Analytics Platform',     'Software',    'Analytics',     2500.00, 800.00),
(102, 'Data Integration Suite',       'Software',    'ETL',           1800.00, 600.00),
(103, 'ML Model Server',              'Software',    'AI/ML',         3200.00, 1100.00),
(104, 'Dashboard Builder Pro',        'Software',    'Visualization', 950.00,  300.00),
(105, 'API Gateway Enterprise',       'Software',    'Infrastructure',1500.00, 500.00),
(106, 'Security Compliance Module',   'Add-on',      'Security',      750.00,  250.00),
(107, 'Real-time Streaming Engine',   'Software',    'Streaming',     2800.00, 950.00),
(108, 'Data Quality Monitor',         'Add-on',      'Governance',    600.00,  200.00),
(109, 'Semantic Layer Connector',     'Add-on',      'Integration',   450.00,  150.00),
(110, 'Enterprise Support Package',   'Service',     'Support',       1200.00, 400.00);

-- 5. Sample Data — Orders (spanning 2024-2025)
INSERT INTO orders VALUES
(1001, 1,  '2024-01-10', 'completed', 'express',  5250.00, 250.00),
(1002, 2,  '2024-01-15', 'completed', 'standard', 1800.00, 0.00),
(1003, 3,  '2024-02-01', 'completed', 'express',  7500.00, 500.00),
(1004, 4,  '2024-02-14', 'completed', 'standard', 3200.00, 0.00),
(1005, 5,  '2024-03-01', 'completed', 'standard', 950.00,  50.00),
(1006, 6,  '2024-03-20', 'completed', 'express',  8750.00, 750.00),
(1007, 7,  '2024-04-05', 'completed', 'standard', 2800.00, 200.00),
(1008, 1,  '2024-04-22', 'completed', 'express',  3200.00, 0.00),
(1009, 8,  '2024-05-10', 'completed', 'standard', 6050.00, 450.00),
(1010, 9,  '2024-05-28', 'completed', 'standard', 600.00,  0.00),
(1011, 10, '2024-06-15', 'completed', 'express',  4300.00, 300.00),
(1012, 11, '2024-06-30', 'completed', 'express',  9500.00, 500.00),
(1013, 2,  '2024-07-12', 'completed', 'standard', 2250.00, 150.00),
(1014, 12, '2024-07-25', 'completed', 'standard', 950.00,  0.00),
(1015, 3,  '2024-08-08', 'completed', 'express',  5600.00, 400.00),
(1016, 13, '2024-08-20', 'completed', 'express',  7200.00, 600.00),
(1017, 4,  '2024-09-01', 'completed', 'standard', 1500.00, 0.00),
(1018, 14, '2024-09-15', 'completed', 'standard', 3650.00, 250.00),
(1019, 5,  '2024-10-01', 'completed', 'standard', 1800.00, 100.00),
(1020, 6,  '2024-10-18', 'completed', 'express',  4500.00, 0.00),
(1021, 15, '2024-11-05', 'completed', 'standard', 2800.00, 200.00),
(1022, 7,  '2024-11-20', 'completed', 'express',  3200.00, 0.00),
(1023, 1,  '2024-12-01', 'completed', 'express',  6800.00, 500.00),
(1024, 8,  '2024-12-15', 'completed', 'standard', 2500.00, 0.00),
(1025, 11, '2025-01-10', 'completed', 'express',  5200.00, 300.00),
(1026, 9,  '2025-01-22', 'completed', 'standard', 1350.00, 0.00),
(1027, 10, '2025-02-05', 'shipped',   'express',  4100.00, 200.00),
(1028, 13, '2025-02-18', 'shipped',   'standard', 3800.00, 0.00),
(1029, 14, '2025-03-01', 'processing','standard', 2950.00, 150.00),
(1030, 15, '2025-03-10', 'processing','express',  1500.00, 0.00);

-- 6. Sample Data — Order Items
INSERT INTO order_items VALUES
(1, 1001, 101, 1, 2500.00, 2500.00),
(2, 1001, 106, 2, 750.00,  1500.00),
(3, 1001, 109, 1, 450.00,  450.00),
(4, 1002, 102, 1, 1800.00, 1800.00),
(5, 1003, 101, 2, 2500.00, 5000.00),
(6, 1003, 105, 1, 1500.00, 1500.00),
(7, 1003, 109, 1, 450.00,  450.00),
(8, 1004, 103, 1, 3200.00, 3200.00),
(9, 1005, 104, 1, 950.00,  950.00),
(10, 1006, 101, 1, 2500.00, 2500.00),
(11, 1006, 103, 1, 3200.00, 3200.00),
(12, 1006, 107, 1, 2800.00, 2800.00),
(13, 1007, 107, 1, 2800.00, 2800.00),
(14, 1008, 103, 1, 3200.00, 3200.00),
(15, 1009, 101, 1, 2500.00, 2500.00),
(16, 1009, 102, 1, 1800.00, 1800.00),
(17, 1009, 106, 1, 750.00,  750.00),
(18, 1009, 108, 1, 600.00,  600.00),
(19, 1010, 108, 1, 600.00,  600.00),
(20, 1011, 103, 1, 3200.00, 3200.00),
(21, 1011, 105, 1, 1500.00, 1500.00),
(22, 1012, 101, 2, 2500.00, 5000.00),
(23, 1012, 103, 1, 3200.00, 3200.00),
(24, 1012, 110, 1, 1200.00, 1200.00),
(25, 1013, 102, 1, 1800.00, 1800.00),
(26, 1013, 109, 1, 450.00,  450.00),
(27, 1014, 104, 1, 950.00,  950.00),
(28, 1015, 101, 1, 2500.00, 2500.00),
(29, 1015, 107, 1, 2800.00, 2800.00),
(30, 1016, 103, 2, 3200.00, 6400.00),
(31, 1016, 106, 1, 750.00,  750.00),
(32, 1017, 105, 1, 1500.00, 1500.00),
(33, 1018, 101, 1, 2500.00, 2500.00),
(34, 1018, 104, 1, 950.00,  950.00),
(35, 1019, 102, 1, 1800.00, 1800.00),
(36, 1020, 101, 1, 2500.00, 2500.00),
(37, 1020, 105, 1, 1500.00, 1500.00),
(38, 1021, 107, 1, 2800.00, 2800.00),
(39, 1022, 103, 1, 3200.00, 3200.00),
(40, 1023, 101, 1, 2500.00, 2500.00),
(41, 1023, 103, 1, 3200.00, 3200.00),
(42, 1023, 110, 1, 1200.00, 1200.00),
(43, 1024, 101, 1, 2500.00, 2500.00),
(44, 1025, 103, 1, 3200.00, 3200.00),
(45, 1025, 107, 1, 2800.00, 2800.00),
(46, 1026, 104, 1, 950.00,  950.00),
(47, 1026, 109, 1, 450.00,  450.00),
(48, 1027, 101, 1, 2500.00, 2500.00),
(49, 1027, 105, 1, 1500.00, 1500.00),
(50, 1028, 103, 1, 3200.00, 3200.00),
(51, 1028, 108, 1, 600.00,  600.00),
(52, 1029, 107, 1, 2800.00, 2800.00),
(53, 1030, 105, 1, 1500.00, 1500.00);

-- 7. Verify
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items;
