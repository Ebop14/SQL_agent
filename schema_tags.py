"""
Schema Tags - Semantic metadata for database columns.

Tags help the agent understand what each column represents,
improving query accuracy by providing business context.
"""

import sqlite3

DB_PATH = "shop.db"

# Tag definitions for each table.column
COLUMN_TAGS = {
    "customers": {
        "id": {
            "tag": "customer_id",
            "description": "Unique identifier for each customer",
            "examples": "1, 2, 3",
            "use_for": "joining with orders, identifying specific customers"
        },
        "name": {
            "tag": "customer_name",
            "description": "Full name of the customer",
            "examples": "Alice Johnson, Bob Smith",
            "use_for": "displaying customer identity, searching by name"
        },
        "email": {
            "tag": "customer_email",
            "description": "Customer's email address (unique)",
            "examples": "alice@email.com",
            "use_for": "contact info, unique customer lookup"
        },
        "city": {
            "tag": "customer_location",
            "description": "City where the customer is located",
            "examples": "New York, Los Angeles, Chicago",
            "use_for": "geographic filtering, location-based analysis"
        },
        "created_at": {
            "tag": "registration_date",
            "description": "When the customer account was created",
            "examples": "2026-01-15 10:30:00",
            "use_for": "customer tenure, cohort analysis, time-based filtering"
        }
    },
    "products": {
        "id": {
            "tag": "product_id",
            "description": "Unique identifier for each product",
            "examples": "1, 2, 3",
            "use_for": "joining with order_items, identifying specific products"
        },
        "name": {
            "tag": "product_name",
            "description": "Name/title of the product",
            "examples": "Laptop, Mouse, Keyboard",
            "use_for": "displaying product identity, searching by name"
        },
        "category": {
            "tag": "product_category",
            "description": "Product category for grouping",
            "examples": "Electronics, Furniture, Office Supplies",
            "use_for": "filtering by type, category analysis, grouping products"
        },
        "price": {
            "tag": "unit_price",
            "description": "Price per unit in dollars",
            "examples": "999.99, 29.99",
            "use_for": "revenue calculations, price filtering, cost analysis"
        },
        "stock": {
            "tag": "inventory_count",
            "description": "Current quantity in stock",
            "examples": "50, 200, 0",
            "use_for": "inventory checks, stock alerts, availability filtering"
        }
    },
    "orders": {
        "id": {
            "tag": "order_id",
            "description": "Unique identifier for each order",
            "examples": "1, 2, 3",
            "use_for": "joining with order_items, identifying specific orders"
        },
        "customer_id": {
            "tag": "ordering_customer",
            "description": "Foreign key to customers table - who placed the order",
            "examples": "1, 2, 3",
            "use_for": "joining with customers, customer order history"
        },
        "order_date": {
            "tag": "purchase_date",
            "description": "When the order was placed",
            "examples": "2026-01-20 14:30:00",
            "use_for": "time-based filtering, sales trends, date range queries"
        },
        "status": {
            "tag": "order_status",
            "description": "Current state of the order",
            "examples": "pending, shipped, delivered",
            "use_for": "filtering by fulfillment state, order tracking"
        }
    },
    "order_items": {
        "id": {
            "tag": "line_item_id",
            "description": "Unique identifier for each order line item",
            "examples": "1, 2, 3",
            "use_for": "identifying specific line items"
        },
        "order_id": {
            "tag": "parent_order",
            "description": "Foreign key to orders - which order this item belongs to",
            "examples": "1, 2, 3",
            "use_for": "joining with orders, grouping items by order"
        },
        "product_id": {
            "tag": "ordered_product",
            "description": "Foreign key to products - which product was ordered",
            "examples": "1, 2, 3",
            "use_for": "joining with products, product sales analysis"
        },
        "quantity": {
            "tag": "quantity_ordered",
            "description": "Number of units ordered",
            "examples": "1, 2, 3",
            "use_for": "calculating totals, volume analysis"
        },
        "unit_price": {
            "tag": "price_at_purchase",
            "description": "Price per unit at time of order (may differ from current product price)",
            "examples": "999.99, 29.99",
            "use_for": "revenue calculations (quantity * unit_price), historical pricing"
        }
    }
}


def create_tags_table(db_path: str = DB_PATH):
    """Create and populate the column_tags metadata table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create metadata table
    cursor.execute("DROP TABLE IF EXISTS column_tags")
    cursor.execute("""
        CREATE TABLE column_tags (
            table_name TEXT NOT NULL,
            column_name TEXT NOT NULL,
            tag TEXT NOT NULL,
            description TEXT,
            examples TEXT,
            use_for TEXT,
            PRIMARY KEY (table_name, column_name)
        )
    """)

    # Insert tag data
    for table, columns in COLUMN_TAGS.items():
        for column, meta in columns.items():
            cursor.execute("""
                INSERT INTO column_tags (table_name, column_name, tag, description, examples, use_for)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                table,
                column,
                meta["tag"],
                meta["description"],
                meta["examples"],
                meta["use_for"]
            ))

    conn.commit()
    conn.close()
    print(f"Created column_tags table with {sum(len(cols) for cols in COLUMN_TAGS.values())} entries")


def get_all_tags(db_path: str = DB_PATH) -> dict:
    """Load all tags from the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT table_name, column_name, tag, description, examples, use_for
        FROM column_tags
        ORDER BY table_name, column_name
    """)

    tags = {}
    for row in cursor.fetchall():
        table, column, tag, desc, examples, use_for = row
        if table not in tags:
            tags[table] = {}
        tags[table][column] = {
            "tag": tag,
            "description": desc,
            "examples": examples,
            "use_for": use_for
        }

    conn.close()
    return tags


def format_tags_for_prompt(tags: dict) -> str:
    """Format tags as a clear reference for the LLM."""
    lines = ["COLUMN TAGS & SEMANTIC METADATA:", "=" * 50]

    for table, columns in tags.items():
        lines.append(f"\n[{table}]")
        for column, meta in columns.items():
            lines.append(f"  {column}:")
            lines.append(f"    tag: {meta['tag']}")
            lines.append(f"    meaning: {meta['description']}")
            lines.append(f"    use for: {meta['use_for']}")

    return "\n".join(lines)


if __name__ == "__main__":
    create_tags_table()

    # Display the tags
    tags = get_all_tags()
    print("\n" + format_tags_for_prompt(tags))
