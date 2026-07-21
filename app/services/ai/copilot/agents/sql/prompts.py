"""
SQL Prompt Templates.

SQL prompt templates for LLM-backed generation.
"""

from __future__ import annotations

SQL_SYSTEM_PROMPT = """
You are an enterprise SQL generation assistant.

Rules:

- Generate valid PostgreSQL SQL.

- Never modify data.

- Never generate UPDATE.

- Never generate DELETE.

- Never generate DROP.

- Never generate INSERT.

Return SQL only.
""".strip()

WAREHOUSE_SCHEMA = """
fact_sales(id, customer_id, product_id, region_id, channel_id, date_id, quantity, amount)
dim_customer(id, customer_code, customer_name)
dim_product(id, product_code, product_name)
dim_region(id, region_name)
dim_channel(id, channel_name)
dim_date(id, full_date)

Relationships:
fact_sales.customer_id = dim_customer.id
fact_sales.product_id = dim_product.id
fact_sales.region_id = dim_region.id
fact_sales.channel_id = dim_channel.id
fact_sales.date_id = dim_date.id
""".strip()
