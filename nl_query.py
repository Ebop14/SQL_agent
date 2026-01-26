"""
Natural Language Query Module for SQL Agent.

Translates natural language questions into SQL queries with full transparency.
Shows the reasoning process, schema analysis, and generated SQL.

Usage:
    # Set your API key in .env file
    ANTHROPIC_API_KEY=your-key-here

    # Run interactive mode
    python nl_query.py --interactive

    # Or run the demo
    python nl_query.py
"""

import anthropic
import json
import os
import re
import sqlite3
from dotenv import load_dotenv
from formatter import Formatter, Colors

# Load environment variables from .env file
load_dotenv()


class NaturalLanguageQueryAgent:
    """
    A transparent SQL agent with natural language query capabilities.

    Features:
    - Translates natural language to SQL via Claude
    - Shows reasoning and set-theory interpretation
    - Displays formatted results as tables
    - Full transparency on every operation
    """

    def __init__(self, db_path: str, api_key: str = None):
        self.db_path = db_path
        self.conn = None
        self.fmt = Formatter()
        self._schema_cache = None

        # Check for API key
        resolved_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not resolved_key:
            raise ValueError(
                "API key required. Either:\n"
                "  1. Add your key to .env file: ANTHROPIC_API_KEY=sk-...\n"
                "  2. Pass api_key parameter\n"
                "  3. Set environment variable: export ANTHROPIC_API_KEY=sk-..."
            )

        self.client = anthropic.Anthropic(api_key=resolved_key)

    def connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def disconnect(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    # =========================================================================
    # SCHEMA EXTRACTION
    # =========================================================================

    def _get_schema_for_llm(self) -> str:
        """Get schema description for the LLM prompt."""
        if self._schema_cache:
            return self._schema_cache

        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]

        schema_parts = ["DATABASE SCHEMA:"]

        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()

            cursor.execute(f"PRAGMA foreign_key_list({table})")
            fks = {fk[3]: f"{fk[2]}.{fk[4]}" for fk in cursor.fetchall()}

            schema_parts.append(f"\nTABLE: {table}")
            schema_parts.append("Columns:")
            for col in columns:
                pk = " [PK]" if col[5] else ""
                fk = f" -> {fks[col[1]]}" if col[1] in fks else ""
                schema_parts.append(f"  - {col[1]}: {col[2]}{pk}{fk}")

        self._schema_cache = "\n".join(schema_parts)
        return self._schema_cache

    def _get_schema_display(self) -> list[dict]:
        """Get schema for formatted display."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]

        result = []
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()

            cursor.execute(f"PRAGMA foreign_key_list({table})")
            fks = {fk[3]: f"{fk[2]}.{fk[4]}" for fk in cursor.fetchall()}

            cols = []
            for col in columns:
                cols.append({
                    "name": col[1],
                    "type": col[2] or "ANY",
                    "pk": bool(col[5]),
                    "fk": fks.get(col[1])
                })

            result.append({"name": table, "columns": cols})

        return result

    # =========================================================================
    # NATURAL LANGUAGE QUERY
    # =========================================================================

    def ask(self, question: str, show_schema: bool = False) -> dict:
        """
        Ask a question in natural language.

        Args:
            question: Natural language question about the data
            show_schema: Whether to display the schema (default False)

        Returns:
            dict with 'sql', 'reasoning', 'results', etc.
        """
        print(self.fmt.header("QUERY"))

        # Step 1: Show the question
        print(self.fmt.step(1, "Question Received", "User input"))
        print(self.fmt.text_block("Input", question, "?"))

        # Step 2: Schema (optional display)
        if show_schema:
            print(self.fmt.step(2, "Database Schema", "sqlite_master + PRAGMA"))
            print(self.fmt.schema_compact(self._get_schema_display()))

        # Step 3: Call LLM
        step_num = 3 if show_schema else 2
        print(self.fmt.step(step_num, "Translating to SQL", "Claude API (claude-sonnet-4-20250514)"))

        schema = self._get_schema_for_llm()
        prompt = self._build_prompt(question, schema)
        response = self._call_llm(prompt)
        parsed = self._parse_response(response)

        # Show reasoning
        if parsed.get('reasoning'):
            print(self.fmt.text_block("Reasoning", parsed['reasoning'], "💭"))

        # Show set theory
        if parsed.get('set_theory'):
            print(self.fmt.text_block("Set Theory", parsed['set_theory'], "∴"))

        # Step 4: Show SQL
        step_num += 1
        print(self.fmt.step(step_num, "Generated SQL", "LLM output"))
        if parsed.get('sql'):
            print(self.fmt.sql(parsed['sql']))
        else:
            print(self.fmt.error("No SQL generated"))
            return parsed

        # Step 5: Execute
        step_num += 1
        print(self.fmt.step(step_num, "Execution", f"SQLite ({self.db_path})"))

        try:
            cursor = self.conn.cursor()
            cursor.execute(parsed['sql'])
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]

            print(self.fmt.table(results))
            print(self.fmt.success("Query completed"))

            parsed['results'] = results
            parsed['success'] = True

        except Exception as e:
            print(self.fmt.error(str(e)))
            parsed['error'] = str(e)
            parsed['success'] = False

        return parsed

    def _build_prompt(self, question: str, schema: str) -> str:
        """Build the LLM prompt."""
        return f"""You are a SQL expert. Translate the natural language question into a SQLite query.

{schema}

QUESTION: {question}

Respond in JSON format:
{{
    "reasoning": "Step-by-step explanation of your interpretation",
    "set_theory": "Explain using set theory (joins as intersections, filters as selections, etc.)",
    "sql": "The SQLite query",
    "explanation": "One-sentence summary"
}}

Rules:
1. Only use tables/columns from the schema
2. Use table aliases in JOINs
3. Be precise - don't return more than asked
4. For ambiguous questions, state assumptions in reasoning

JSON only, no other text."""

    def _call_llm(self, prompt: str) -> str:
        """Call Claude API."""
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def _parse_response(self, response: str) -> dict:
        """Parse the LLM JSON response."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON
            match = re.search(r'\{[\s\S]*\}', response)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            return {
                'sql': None,
                'reasoning': response,
                'error': 'Failed to parse LLM response'
            }

    # =========================================================================
    # INTERACTIVE MODE
    # =========================================================================

    def interactive(self):
        """Run interactive query session."""
        print(self.fmt.header("SQL AGENT"))
        print(f"""
    {Colors.BOLD}Natural Language Database Query Agent{Colors.RESET}

    Commands:
      • Type a question in plain English
      • {Colors.CYAN}schema{Colors.RESET}  - Show database structure
      • {Colors.CYAN}help{Colors.RESET}    - Show example questions
      • {Colors.CYAN}quit{Colors.RESET}    - Exit
""")

        while True:
            try:
                print(f"\n{Colors.GREEN}?{Colors.RESET} ", end="")
                question = input().strip()

                if not question:
                    continue
                if question.lower() == 'quit':
                    print(f"\n{Colors.DIM}Goodbye!{Colors.RESET}\n")
                    break
                if question.lower() == 'schema':
                    print(self.fmt.header("DATABASE SCHEMA"))
                    print(self.fmt.schema_compact(self._get_schema_display()))
                    continue
                if question.lower() == 'help':
                    self._show_help()
                    continue

                self.ask(question)

            except KeyboardInterrupt:
                print(f"\n\n{Colors.DIM}Goodbye!{Colors.RESET}\n")
                break
            except Exception as e:
                print(self.fmt.error(str(e)))

    def _show_help(self):
        """Show example questions."""
        print(self.fmt.header("EXAMPLE QUESTIONS"))
        examples = """
    {bold}Basic Queries:{reset}
      • How many customers do we have?
      • What products are in the Electronics category?
      • Show me all pending orders

    {bold}Aggregations:{reset}
      • What is the average product price?
      • How many orders does each customer have?
      • What's the total revenue by category?

    {bold}Joins & Relationships:{reset}
      • Which customers have placed orders?
      • What products has Alice ordered?
      • Show order details with customer and product names

    {bold}Complex Queries:{reset}
      • Who are our top 3 customers by spending?
      • What products have never been ordered?
      • What's the average order value per customer?
""".format(bold=Colors.BOLD, reset=Colors.RESET)
        print(examples)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        with NaturalLanguageQueryAgent("shop.db") as agent:
            agent.interactive()
    else:
        # Demo mode
        with NaturalLanguageQueryAgent("shop.db") as agent:
            print(Formatter.header("SQL AGENT DEMO"))

            questions = [
                "How many customers do we have?",
                "Who are the top 3 customers by total spending?",
            ]

            for q in questions:
                agent.ask(q)
                print("\n")


if __name__ == "__main__":
    main()
