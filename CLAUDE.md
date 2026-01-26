# SQL Agent

A transparent SQL agent that translates natural language questions into SQL queries.

## Project Structure

```
SQL_agent/
├── nl_query.py        # Main agent - natural language to SQL
├── sql_agent.py       # Base SQL agent with transparency logging
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

# Create the sample database
python setup_database.py
```

## Usage

### Interactive Mode
```bash
python nl_query.py --interactive
```

### Demo Mode
```bash
python nl_query.py
```

## Database Schema

The sample database (`shop.db`) contains:

- **customers** - id, name, email, city, created_at
- **products** - id, name, category, price, stock
- **orders** - id, customer_id (FK), order_date, status
- **order_items** - id, order_id (FK), product_id (FK), quantity, unit_price

## Features

### Transparency
Every query shows:
1. The input question
2. LLM reasoning process
3. Set theory interpretation
4. Generated SQL (syntax highlighted)
5. Execution results (formatted table)

### Set Theory
The agent explains queries using set theory concepts:
- JOINs as set intersections
- WHERE as selection predicates
- GROUP BY as partitioning
- Aggregations as functions over partitions

## Dependencies

- `anthropic` - Claude API client
- `python-dotenv` - Environment variable loading
