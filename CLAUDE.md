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
| `customers.city` | `customer_location` | Geographic filtering |
| `order_items.unit_price` | `price_at_purchase` | Revenue calculations (historical price) |
| `products.category` | `product_category` | Category analysis, grouping |

To add or modify tags, edit `schema_tags.py` and re-run it.

## Database Schema

The sample database (`shop.db`) contains:

- **customers** - id, name, email, city, created_at
- **products** - id, name, category, price, stock
- **orders** - id, customer_id (FK), order_date, status
- **order_items** - id, order_id (FK), product_id (FK), quantity, unit_price
- **column_tags** - table_name, column_name, tag, description, examples, use_for

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
