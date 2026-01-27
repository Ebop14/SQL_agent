# SQL Agent

A transparent SQL agent that translates natural language questions into SQL queries.

## Project Structure

```
SQL_agent/
├── nl_query.py        # Main agent - natural language to SQL
├── sql_agent.py       # Base SQL agent with transparency logging
├── schema_tags.py     # Column tags & semantic metadata
├── formatter.py       # Terminal output formatting (colors, tables, boxes)
├── setup_database.py  # Creates sample SQLite database
├── requirements.txt   # Python dependencies
├── .env               # API key (git-ignored)
├── .env.example       # Template for .env
└── shop.db            # SQLite database (git-ignored)
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Add your Anthropic API key to .env
cp .env.example .env
# Edit .env and add your key

# Create the sample database and column tags
python setup_database.py
python schema_tags.py
```

## Usage

### Interactive Mode
```bash
python nl_query.py --interactive
```

Commands:
- Type any question in plain English
- `schema` - Show database structure
- `tags` - Show column tags & meanings
- `help` - Show example questions
- `quit` - Exit

### Demo Mode
```bash
python nl_query.py
```

## Column Tags

Before every query, the agent reads semantic tags from the `column_tags` table. Tags provide:
- **tag**: Short semantic identifier (e.g., `customer_location`)
- **description**: What the column means in business terms
- **use_for**: When to use this column (joins, filters, aggregations)

Example tags:
| Column | Tag | Use For |
|--------|-----|---------|
| `customers.membership_tier` | `customer_tier` | VIP filtering, loyalty analysis |
| `customers.total_spent` | `customer_lifetime_value` | High-value customer identification |
| `order_items.unit_price` | `price_at_purchase` | Revenue calculations (historical price) |
| `products.rating` | `product_rating` | Quality filtering, top-rated products |
| `orders.total_amount` | `order_total` | Revenue calculations, order value analysis |
| `reviews.verified_purchase` | `review_verified` | Filtering trustworthy reviews |

To add or modify tags, edit `schema_tags.py` and re-run it.

## Database Schema

The sample database (`shop.db`) contains ~26,000 rows across 12 tables:

### Core Tables
- **categories** (12 rows) - id, name, description, parent_category_id, created_at
- **customers** (1,000 rows) - id, first_name, last_name, email, phone, address, city, state, postal_code, country, date_of_birth, gender, membership_tier, loyalty_points, total_spent, order_count, preferred_payment, newsletter_subscribed, account_status, last_login, created_at
- **products** (309 rows) - id, sku, name, description, category_id (FK), brand, price, cost, weight, stock, reorder_level, supplier_id (FK), rating, review_count, is_active, is_featured, created_at, updated_at

### Order Management
- **orders** (5,000 rows) - id, order_number, customer_id (FK), employee_id (FK), order_date, required_date, shipped_date, status, shipping_method_id (FK), shipping_address, shipping_city, shipping_state, shipping_postal_code, shipping_country, subtotal, shipping_cost, tax_amount, discount_amount, total_amount, payment_method, payment_status, discount_code_id (FK), notes, created_at
- **order_items** (12,981 rows) - id, order_id (FK), product_id (FK), quantity, unit_price, discount_pct, line_total

### Supporting Tables
- **employees** (150 rows) - id, first_name, last_name, email, phone, department_id (FK), manager_id (FK), hire_date, salary, commission_pct, active, created_at
- **departments** (8 rows) - id, name, description, budget, created_at
- **suppliers** (10 rows) - id, name, email, phone, address, city, state, country, rating, active, created_at
- **reviews** (3,000 rows) - id, product_id (FK), customer_id (FK), order_id (FK), rating, title, comment, helpful_votes, verified_purchase, created_at
- **inventory_log** (3,838 rows) - id, product_id (FK), change_type, quantity_change, quantity_after, reference_type, reference_id, notes, created_at
- **shipping_methods** (5 rows) - id, name, price, min_days, max_days, is_active
- **discount_codes** (8 rows) - id, code, discount_value, discount_type, valid_from, valid_until, minimum_order, usage_count, max_uses, is_active
- **column_tags** (134 rows) - table_name, column_name, tag, description, examples, use_for

## Features

### Transparency
Every query shows:
1. The input question
2. Column tags loaded (with count)
3. LLM reasoning process
4. Set theory interpretation
5. Which tags were used
6. Generated SQL (syntax highlighted)
7. Execution results (formatted table)

### Set Theory
The agent explains queries using set theory concepts:
- JOINs as set intersections
- WHERE as selection predicates
- GROUP BY as partitioning
- Aggregations as functions over partitions

## Dependencies

- `anthropic` - Claude API client
- `python-dotenv` - Environment variable loading
