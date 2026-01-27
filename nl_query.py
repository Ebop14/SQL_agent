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
from formatter import Formatter, Colors, spinner
from schema_tags import get_all_tags, format_tags_for_prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML

# Load environment variables from .env file
load_dotenv()


class NaturalLanguageQueryAgent:
    """
    A transparent SQL agent with natural language query capabilities.

    Features:
    - Translates natural language to SQL via Claude
    - Uses semantic column tags for better understanding
    - Shows reasoning and set-theory interpretation
    - Displays formatted results as tables
    - Full transparency on every operation (toggle with Cmd+O)
    """

    def __init__(self, db_path: str, api_key: str = None):
        self.db_path = db_path
        self.conn = None
        self.fmt = Formatter()
        self._schema_cache = None
        self._tags_cache = None
        self.verbose = False  # Hide intermediate steps by default

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
    # TAGS & SCHEMA
    # =========================================================================

    def _load_tags(self) -> dict:
        """Load column tags from database."""
        if self._tags_cache is not None:
            return self._tags_cache

        try:
            self._tags_cache = get_all_tags(self.db_path)
        except Exception:
            # Tags table might not exist yet
            self._tags_cache = {}

        return self._tags_cache

    def _get_tags_for_prompt(self) -> str:
        """Get formatted tags for LLM prompt."""
        tags = self._load_tags()
        if not tags:
            return ""
        return format_tags_for_prompt(tags)

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
        # Verbose mode shows all steps; compact mode shows only answer + limitations
        verbose = self.verbose

        if verbose:
            print(self.fmt.header("QUERY"))

            # Step 1: Show the question
            print(self.fmt.step(1, "Question Received", "User input"))
            print(self.fmt.text_block("Input", question, "?"))

        # Step 2: Load column tags
        if verbose:
            print(self.fmt.step(2, "Reading Column Tags", "column_tags table"))
        tags = self._load_tags()
        tag_count = sum(len(cols) for cols in tags.values())
        if verbose:
            if tag_count > 0:
                tables_with_tags = list(tags.keys())
                print(self.fmt.text_block("Loaded", f"{tag_count} column tags from {len(tables_with_tags)} tables: {', '.join(tables_with_tags)}", "📑"))
            else:
                print(self.fmt.text_block("Warning", "No column tags found. Run: python schema_tags.py", "⚠"))

        # Step 3: Schema (optional display)
        step_num = 3
        if show_schema and verbose:
            print(self.fmt.step(step_num, "Database Schema", "sqlite_master + PRAGMA"))
            print(self.fmt.schema_compact(self._get_schema_display()))
            step_num += 1

        # Step 4: Call LLM
        if verbose:
            print(self.fmt.step(step_num, "Translating to SQL", "Claude API (claude-sonnet-4-20250514)"))

        schema = self._get_schema_for_llm()
        tags_prompt = self._get_tags_for_prompt()
        prompt = self._build_prompt(question, schema, tags_prompt)
        with spinner("writing"):
            response = self._call_llm(prompt)
        parsed = self._parse_response(response)

        # Show reasoning (verbose only)
        if verbose and parsed.get('reasoning'):
            print(self.fmt.text_block("Reasoning", parsed['reasoning'], "💭"))

        # Show set theory (verbose only)
        if verbose and parsed.get('set_theory'):
            print(self.fmt.text_block("Set Theory", parsed['set_theory'], "∴"))

        # Show which tags were used (verbose only)
        if verbose and parsed.get('tags_used'):
            print(self.fmt.text_block("Tags Used", parsed['tags_used'], "🏷"))

        # Step: Show SQL (verbose only)
        step_num += 1
        if verbose:
            print(self.fmt.step(step_num, "Generated SQL", "LLM output"))
        if parsed.get('sql'):
            if verbose:
                print(self.fmt.sql(parsed['sql']))
        else:
            print(self.fmt.error("No SQL generated"))
            return parsed

        # Step: Execute
        step_num += 1
        if verbose:
            print(self.fmt.step(step_num, "Execution", f"SQLite ({self.db_path})"))

        try:
            cursor = self.conn.cursor()
            cursor.execute(parsed['sql'])
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]

            if verbose:
                print(self.fmt.table(results))

            parsed['results'] = results
            parsed['success'] = True

        except Exception as e:
            print(self.fmt.error(str(e)))
            parsed['error'] = str(e)
            parsed['success'] = False
            return parsed

        # Step: Interpretation
        step_num += 1
        if verbose:
            print(self.fmt.step(step_num, "Interpretation", "Claude API"))

        with spinner("reading"):
            interpretation = self._interpret_results(
                question=question,
                sql=parsed.get('sql', ''),
                results=results,
                reasoning=parsed.get('reasoning', '')
            )

        # Always show Answer and Limitations
        if interpretation.get('summary'):
            print(self.fmt.text_block("Answer", interpretation['summary'], "💬"))

        if interpretation.get('limitations'):
            print(self.fmt.text_block("Limitations", interpretation['limitations'], "⚠"))

        parsed['interpretation'] = interpretation

        return parsed

    def _build_prompt(self, question: str, schema: str, tags: str = "") -> str:
        """Build the LLM prompt with schema and semantic tags."""
        tags_section = f"\n{tags}\n" if tags else ""

        return f"""You are a SQL expert. Translate the natural language question into a SQLite query.

{schema}
{tags_section}
QUESTION: {question}

The COLUMN TAGS above provide semantic meaning for each column. Use them to:
- Understand what each column represents in business terms
- Choose the right columns for the query
- Identify which columns to use for joins, filters, and aggregations

Respond in JSON format:
{{
    "reasoning": "Step-by-step explanation of your interpretation",
    "set_theory": "Explain using set theory (joins as intersections, filters as selections, etc.)",
    "tags_used": "List the column tags that were most relevant (e.g., 'customer_name, total_spending')",
    "sql": "The SQLite query",
    "explanation": "One-sentence summary"
}}

Rules:
1. Only use tables/columns from the schema
2. Use table aliases in JOINs
3. Be precise - don't return more than asked
4. Reference the column tags to understand what data means

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

    def _interpret_results(self, question: str, sql: str, results: list, reasoning: str) -> dict:
        """Generate a natural language interpretation of the results."""
        # Limit results shown to LLM to avoid token limits
        results_preview = results[:20] if len(results) > 20 else results
        results_note = f" (showing first 20 of {len(results)})" if len(results) > 20 else ""

        prompt = f"""You are a data analyst explaining query results to a business user.

ORIGINAL QUESTION: {question}

SQL EXECUTED:
{sql}

QUERY REASONING: {reasoning}

RESULTS{results_note}:
{json.dumps(results_preview, indent=2, default=str)}

Provide a natural language interpretation. Respond in JSON:
{{
    "summary": "A direct, conversational answer to the question. Use specific numbers and names from the results. Be concise but complete. Examples: 'You have 5 customers in the database.' or 'Carol Williams is your top customer with $6,518.73 in total spending, followed by Eva Martinez ($3,953.79) and Alice Johnson ($3,502.85).'",
    "limitations": "Note any caveats, edge cases, or potential issues with interpreting these results. Consider: data freshness, what the query doesn't account for (returns, cancellations, time periods), assumptions made, potential for misleading conclusions. If there are no significant limitations, use null."
}}

Be specific and actionable. If there are no results, explain what that means.
JSON only, no other text."""

        try:
            response = self._call_llm(prompt)
            return self._parse_response(response)
        except Exception as e:
            return {
                'summary': f"Results returned {len(results)} row(s).",
                'limitations': f"Could not generate interpretation: {str(e)}"
            }

    # =========================================================================
    # INTERACTIVE MODE
    # =========================================================================

    def interactive(self):
        """Run interactive query session."""
        print(self.fmt.header("SQL AGENT"))
        verbose_status = f"{Colors.GREEN}ON{Colors.RESET}" if self.verbose else f"{Colors.DIM}OFF{Colors.RESET}"
        print(f"""
    {Colors.BOLD}Natural Language Database Query Agent{Colors.RESET}

    Commands:
      • Type a question in plain English
      • {Colors.CYAN}schema{Colors.RESET}   - Show database structure
      • {Colors.CYAN}tags{Colors.RESET}     - Show column tags & meanings
      • {Colors.CYAN}verbose{Colors.RESET}  - Toggle verbose mode [{verbose_status}{Colors.RESET}]
      • {Colors.CYAN}help{Colors.RESET}     - Show example questions
      • {Colors.CYAN}quit{Colors.RESET}     - Exit

    {Colors.DIM}Ctrl+O toggle verbose • Tab auto-fill • Cmd+Z undo{Colors.RESET}
""")

        # Example prompts that cycle through
        examples = [
            "How many customers do we have?",
            "What products are in the Electronics category?",
            "Show me all pending orders",
            "Who are our top 3 customers by spending?",
            "What's the total revenue by category?",
            "Which customers have placed orders?",
            "What products have never been ordered?",
            "What's the average order value per customer?",
        ]
        example_index = [0]  # Use list to allow mutation in closure

        # Set up key bindings
        bindings = KeyBindings()

        # Reference to self for use in closure
        agent = self

        @bindings.add('tab')
        def accept_placeholder(event):
            """Tab inserts the current example if buffer is empty."""
            buf = event.app.current_buffer
            if not buf.text:
                buf.insert_text(examples[example_index[0]])

        @bindings.add('c-o')  # Cmd+O on Mac (interpreted as Ctrl+O)
        def toggle_verbose(event):
            """Toggle verbose mode."""
            agent.verbose = not agent.verbose
            status = f"{Colors.GREEN}ON{Colors.RESET}" if agent.verbose else f"{Colors.DIM}OFF{Colors.RESET}"
            print(f"\n    {Colors.CYAN}Verbose mode:{Colors.RESET} {status}")
            if agent.verbose:
                print(f"    {Colors.DIM}All steps will be shown{Colors.RESET}")
            else:
                print(f"    {Colors.DIM}Only Answer + Limitations will be shown{Colors.RESET}")

        # Set up prompt styling and history
        prompt_style = Style.from_dict({
            'prompt': 'ansigreen bold',
            'placeholder': 'ansigray',
        })

        # Store history in user's home directory
        history_file = os.path.expanduser("~/.sql_agent_history")
        history = FileHistory(history_file)

        # Create session for persistent settings
        session = PromptSession(
            history=history,
            enable_history_search=True,
            key_bindings=bindings,
            style=prompt_style,
        )

        while True:
            try:
                # Get current placeholder
                current_example = examples[example_index[0]]
                placeholder = HTML(f'<placeholder>{current_example}</placeholder>')

                question = session.prompt(
                    [('class:prompt', '? ')],
                    placeholder=placeholder,
                ).strip()

                # Cycle to next example for next prompt
                example_index[0] = (example_index[0] + 1) % len(examples)

                if not question:
                    continue
                if question.lower() == 'quit':
                    print(f"\n{Colors.DIM}Goodbye!{Colors.RESET}\n")
                    break
                if question.lower() == 'schema':
                    print(self.fmt.header("DATABASE SCHEMA"))
                    print(self.fmt.schema_compact(self._get_schema_display()))
                    continue
                if question.lower() == 'tags':
                    self._show_tags()
                    continue
                if question.lower() == 'help':
                    self._show_help()
                    continue
                if question.lower() == 'verbose':
                    self.verbose = not self.verbose
                    status = f"{Colors.GREEN}ON{Colors.RESET}" if self.verbose else f"{Colors.DIM}OFF{Colors.RESET}"
                    print(f"\n    {Colors.CYAN}Verbose mode:{Colors.RESET} {status}")
                    if self.verbose:
                        print(f"    {Colors.DIM}All steps will be shown{Colors.RESET}")
                    else:
                        print(f"    {Colors.DIM}Only Answer + Limitations will be shown{Colors.RESET}")
                    continue

                self.ask(question)

            except KeyboardInterrupt:
                print(f"\n\n{Colors.DIM}Goodbye!{Colors.RESET}\n")
                break
            except EOFError:
                print(f"\n{Colors.DIM}Goodbye!{Colors.RESET}\n")
                break
            except Exception as e:
                print(self.fmt.error(str(e)))

    def _show_tags(self):
        """Show all column tags."""
        print(self.fmt.header("COLUMN TAGS"))
        tags = self._load_tags()

        if not tags:
            print(f"\n    {Colors.YELLOW}No tags found.{Colors.RESET}")
            print(f"    Run: {Colors.CYAN}python schema_tags.py{Colors.RESET} to create them.\n")
            return

        for table, columns in tags.items():
            print(f"\n    {Colors.BOLD}{table}{Colors.RESET}")
            print(f"    {Colors.DIM}{'─' * 50}{Colors.RESET}")
            for col, meta in columns.items():
                print(f"      {Colors.CYAN}{col}{Colors.RESET} → {Colors.YELLOW}{meta['tag']}{Colors.RESET}")
                print(f"        {Colors.DIM}{meta['description']}{Colors.RESET}")
                print(f"        {Colors.DIM}Use for: {meta['use_for']}{Colors.RESET}")

    def _show_help(self):
        """Show example questions."""
        print(self.fmt.header("HELP"))
        verbose_status = f"{Colors.GREEN}ON{Colors.RESET}" if self.verbose else f"{Colors.DIM}OFF{Colors.RESET}"
        help_text = """
    {bold}Output Mode:{reset}
      • {cyan}verbose{reset} - Toggle detailed output [{verbose_status}{reset}]
      • {cyan}Ctrl+O{reset} - Keyboard shortcut for verbose toggle

      {dim}Verbose OFF: Shows only Answer + Limitations
      Verbose ON:  Shows all steps (tags, reasoning, SQL, results){reset}

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
""".format(bold=Colors.BOLD, reset=Colors.RESET, cyan=Colors.CYAN, dim=Colors.DIM, verbose_status=verbose_status)
        print(help_text)


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
