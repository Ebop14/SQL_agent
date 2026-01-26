"""
SQL Agent - A transparent database interaction agent.

This agent provides full visibility into:
- What operations it performs
- The SQL statements it executes
- Where information comes from
- Set-theory reasoning behind queries
"""

import sqlite3
from typing import Optional


class SQLAgent:
    """
    An agent that interacts with SQLite databases with full transparency.

    Every operation is logged and explained, including:
    - The reasoning behind the query
    - The SQL statement being executed
    - The source of all information
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._log_action("INITIALIZE", f"Agent created for database: {db_path}")

    # =========================================================================
    # LOGGING & TRANSPARENCY
    # =========================================================================

    def _log_action(self, action_type: str, message: str):
        """Log an action with clear formatting."""
        print(f"\n[{action_type}] {message}")

    def _log_sql(self, sql: str, params: tuple = None):
        """Log SQL statement before execution."""
        print("\n" + "-" * 50)
        print("SQL STATEMENT:")
        print("-" * 50)
        print(sql.strip())
        if params:
            print(f"\nParameters: {params}")
        print("-" * 50)

    def _log_reasoning(self, reasoning: str):
        """Log the reasoning/set-theory behind a query."""
        print("\n💭 REASONING:")
        for line in reasoning.split("\n"):
            print(f"   {line}")

    def _log_source(self, source: str):
        """Log where information came from."""
        print(f"\n📍 SOURCE: {source}")

    def _log_result(self, result):
        """Log query results."""
        print("\n📊 RESULT:")
        if isinstance(result, list):
            if len(result) == 0:
                print("   (no rows returned)")
            else:
                for row in result:
                    print(f"   {row}")
        else:
            print(f"   {result}")

    # =========================================================================
    # CONNECTION MANAGEMENT
    # =========================================================================

    def connect(self):
        """Establish database connection."""
        self._log_action("CONNECT", f"Opening connection to {self.db_path}")
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        self._log_action("CONNECT", "Connection established successfully")

    def disconnect(self):
        """Close database connection."""
        if self.conn:
            self._log_action("DISCONNECT", "Closing database connection")
            self.conn.close()
            self.conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    # =========================================================================
    # DATABASE INTROSPECTION
    # =========================================================================

    def describe_database(self):
        """
        Describe the entire database structure.
        Shows all tables, their columns, and relationships.
        """
        self._log_action("DESCRIBE DATABASE", "Analyzing database structure")
        self._log_source("SQLite system table: sqlite_master")

        # Get all tables
        sql = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        self._log_sql(sql)

        cursor = self.conn.cursor()
        cursor.execute(sql)
        tables = [row[0] for row in cursor.fetchall()]

        print("\n" + "=" * 60)
        print("DATABASE STRUCTURE")
        print("=" * 60)

        for table in tables:
            self._describe_table(table)

        # Show relationships
        self._show_relationships()

    def _describe_table(self, table_name: str):
        """Describe a single table's structure."""
        self._log_source(f"PRAGMA table_info({table_name})")

        sql = f"PRAGMA table_info({table_name})"
        self._log_sql(sql)

        cursor = self.conn.cursor()
        cursor.execute(sql)
        columns = cursor.fetchall()

        print(f"\n📋 TABLE: {table_name}")
        print("   " + "-" * 40)
        print(f"   {'Column':<20} {'Type':<15} {'Nullable':<10} {'PK'}")
        print("   " + "-" * 40)

        for col in columns:
            # col: (cid, name, type, notnull, dflt_value, pk)
            nullable = "NO" if col[3] else "YES"
            pk = "✓" if col[5] else ""
            print(f"   {col[1]:<20} {col[2]:<15} {nullable:<10} {pk}")

        # Get row count
        count_sql = f"SELECT COUNT(*) FROM {table_name}"
        cursor.execute(count_sql)
        count = cursor.fetchone()[0]
        print(f"\n   Row count: {count}")

    def _show_relationships(self):
        """Show foreign key relationships between tables."""
        self._log_action("ANALYZE", "Finding foreign key relationships")

        sql = "SELECT name FROM sqlite_master WHERE type='table'"
        cursor = self.conn.cursor()
        cursor.execute(sql)
        tables = [row[0] for row in cursor.fetchall()]

        print("\n🔗 RELATIONSHIPS (Foreign Keys):")
        print("   " + "-" * 50)

        found_any = False
        for table in tables:
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            fks = cursor.fetchall()
            for fk in fks:
                # fk: (id, seq, table, from, to, on_update, on_delete, match)
                print(f"   {table}.{fk[3]} → {fk[2]}.{fk[4]}")
                found_any = True

        if not found_any:
            print("   (no foreign keys defined)")

    def list_tables(self) -> list:
        """List all tables in the database."""
        self._log_action("LIST TABLES", "Retrieving all table names")
        self._log_source("SQLite system table: sqlite_master")

        sql = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        self._log_sql(sql)

        cursor = self.conn.cursor()
        cursor.execute(sql)
        tables = [row[0] for row in cursor.fetchall()]

        self._log_result(tables)
        return tables

    # =========================================================================
    # SQL OPERATIONS
    # =========================================================================

    def execute_select(self, sql: str, params: tuple = None, reasoning: str = None):
        """
        Execute a SELECT query with full transparency.

        Args:
            sql: The SELECT statement to execute
            params: Optional parameters for parameterized queries
            reasoning: Optional explanation of the query logic
        """
        self._log_action("SELECT", "Executing read query")

        if reasoning:
            self._log_reasoning(reasoning)

        self._log_sql(sql, params)

        cursor = self.conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        rows = cursor.fetchall()

        # Get column names
        columns = [description[0] for description in cursor.description]
        print(f"\n📊 COLUMNS: {columns}")

        # Convert to list of dicts for readability
        results = [dict(zip(columns, row)) for row in rows]
        self._log_result(results)

        return results

    def execute_insert(self, sql: str, params: tuple = None, reasoning: str = None):
        """Execute an INSERT statement with full transparency."""
        self._log_action("INSERT", "Executing insert operation")

        if reasoning:
            self._log_reasoning(reasoning)

        self._log_sql(sql, params)

        cursor = self.conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        self.conn.commit()
        self._log_action("INSERT", f"Inserted row with ID: {cursor.lastrowid}")
        self._log_action("COMMIT", "Changes committed to database")

        return cursor.lastrowid

    def execute_update(self, sql: str, params: tuple = None, reasoning: str = None):
        """Execute an UPDATE statement with full transparency."""
        self._log_action("UPDATE", "Executing update operation")

        if reasoning:
            self._log_reasoning(reasoning)

        self._log_sql(sql, params)

        cursor = self.conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        self.conn.commit()
        self._log_action("UPDATE", f"Rows affected: {cursor.rowcount}")
        self._log_action("COMMIT", "Changes committed to database")

        return cursor.rowcount

    def execute_delete(self, sql: str, params: tuple = None, reasoning: str = None):
        """Execute a DELETE statement with full transparency."""
        self._log_action("DELETE", "Executing delete operation")

        if reasoning:
            self._log_reasoning(reasoning)

        self._log_sql(sql, params)

        cursor = self.conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        self.conn.commit()
        self._log_action("DELETE", f"Rows deleted: {cursor.rowcount}")
        self._log_action("COMMIT", "Changes committed to database")

        return cursor.rowcount

    # =========================================================================
    # SET THEORY OPERATIONS
    # =========================================================================

    def explain_set_theory(self, operation: str):
        """
        Explain SQL operations in terms of set theory.

        SQL is fundamentally based on relational algebra, which is rooted in set theory.
        This method explains how SQL operations map to set operations.
        """
        explanations = {
            "SELECT": """
SELECT = PROJECTION (π) + SELECTION (σ)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• PROJECTION (columns): Choosing which attributes to include
  - Set theory: Creates a new set with only specified attributes
  - SQL: SELECT column1, column2 FROM table

• SELECTION (rows): Filtering based on conditions
  - Set theory: Creates a subset where predicate is true
  - SQL: SELECT * FROM table WHERE condition
            """,

            "JOIN": """
JOIN = CARTESIAN PRODUCT (×) + SELECTION (σ)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• INNER JOIN: Intersection based on matching keys
  - Set theory: A ∩ B where keys match
  - SQL: SELECT * FROM A INNER JOIN B ON A.id = B.a_id

• LEFT JOIN: All of A plus matching B
  - Set theory: A ∪ (A ∩ B), with NULLs for non-matches
  - SQL: SELECT * FROM A LEFT JOIN B ON A.id = B.a_id

• CROSS JOIN: Cartesian product
  - Set theory: A × B (all combinations)
  - SQL: SELECT * FROM A CROSS JOIN B
            """,

            "UNION": """
UNION = SET UNION (∪)
━━━━━━━━━━━━━━━━━━━━━
• UNION: Combines results, removes duplicates
  - Set theory: A ∪ B
  - SQL: SELECT * FROM A UNION SELECT * FROM B

• UNION ALL: Combines results, keeps duplicates
  - Multiset union (not pure set theory)
  - SQL: SELECT * FROM A UNION ALL SELECT * FROM B
            """,

            "INTERSECT": """
INTERSECT = SET INTERSECTION (∩)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Returns only rows that appear in both result sets
• Set theory: A ∩ B
• SQL: SELECT * FROM A INTERSECT SELECT * FROM B
            """,

            "EXCEPT": """
EXCEPT = SET DIFFERENCE (−)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Returns rows in A that are not in B
• Set theory: A − B (or A \\ B)
• SQL: SELECT * FROM A EXCEPT SELECT * FROM B
            """,

            "GROUP BY": """
GROUP BY = PARTITIONING
━━━━━━━━━━━━━━━━━━━━━━━━
• Partitions the set into equivalence classes
• Each group is a subset where all rows share the same key value
• Aggregate functions (SUM, COUNT, AVG) operate on each partition
• Set theory: Creates partition P = {S₁, S₂, ..., Sₙ} where ∪Sᵢ = S
            """
        }

        self._log_action("SET THEORY", f"Explaining '{operation}' in set-theoretic terms")

        if operation.upper() in explanations:
            print(explanations[operation.upper()])
        else:
            print(f"No set-theory explanation available for '{operation}'")
            print("Available explanations: SELECT, JOIN, UNION, INTERSECT, EXCEPT, GROUP BY")

    # =========================================================================
    # CAPABILITIES
    # =========================================================================

    def show_capabilities(self):
        """Display what this agent can do."""
        print("\n" + "=" * 60)
        print("SQL AGENT CAPABILITIES")
        print("=" * 60)

        capabilities = """
🔍 READ OPERATIONS:
   • describe_database() - Show full database structure
   • list_tables() - List all tables
   • execute_select(sql, params, reasoning) - Run SELECT queries

✏️  WRITE OPERATIONS:
   • execute_insert(sql, params, reasoning) - Insert new rows
   • execute_update(sql, params, reasoning) - Update existing rows
   • execute_delete(sql, params, reasoning) - Delete rows

🧠 SET THEORY:
   • explain_set_theory(operation) - Explain SQL in set-theoretic terms

📊 INTROSPECTION:
   • _describe_table(name) - Describe a specific table
   • _show_relationships() - Show foreign key relationships

🔐 TRANSPARENCY GUARANTEES:
   • Every SQL statement is logged before execution
   • All reasoning is documented
   • Data sources are clearly identified
   • Results are displayed after each operation
"""
        print(capabilities)


# =============================================================================
# DEMO USAGE
# =============================================================================

def demo():
    """Demonstrate the SQL agent's capabilities."""
    print("\n" + "=" * 60)
    print("SQL AGENT DEMONSTRATION")
    print("=" * 60)

    with SQLAgent("shop.db") as agent:
        # Show capabilities
        agent.show_capabilities()

        # Describe the database
        agent.describe_database()

        # Explain set theory for JOINs
        agent.explain_set_theory("JOIN")

        # Example query with reasoning
        agent.execute_select(
            """
            SELECT c.name, COUNT(o.id) as order_count
            FROM customers c
            LEFT JOIN orders o ON c.id = o.customer_id
            GROUP BY c.id, c.name
            ORDER BY order_count DESC
            """,
            reasoning="""
Set-theoretic approach:
1. Start with the CUSTOMERS set (all customers)
2. LEFT JOIN with ORDERS: This is A ∪ (A ∩ B) where A=customers, B=orders
   - Keeps all customers even if they have no orders
3. GROUP BY partitions the result into equivalence classes by customer
4. COUNT aggregates each partition to find order counts
5. ORDER BY sorts the final set by the aggregated value
"""
        )


if __name__ == "__main__":
    demo()
