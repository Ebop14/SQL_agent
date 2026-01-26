"""
Output Formatter for SQL Agent.

Provides clean, structured terminal output with:
- Box drawing for sections
- Formatted tables for results
- Syntax highlighting for SQL
- Clean JSON display
"""

import re
import textwrap
from typing import Any


# Terminal width
WIDTH = 70


class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Colors
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"


class Formatter:
    """Formats output for the SQL agent."""

    @staticmethod
    def header(title: str, char: str = "═") -> str:
        """Create a section header."""
        line = char * WIDTH
        return f"\n{Colors.BLUE}{line}{Colors.RESET}\n{Colors.BOLD}{title}{Colors.RESET}\n{Colors.BLUE}{line}{Colors.RESET}"

    @staticmethod
    def subheader(title: str) -> str:
        """Create a subsection header."""
        return f"\n{Colors.CYAN}┌─ {title} {'─' * (WIDTH - len(title) - 4)}┐{Colors.RESET}"

    @staticmethod
    def step(num: int, title: str, source: str = None) -> str:
        """Format a numbered step."""
        output = f"\n{Colors.YELLOW}[{num}]{Colors.RESET} {Colors.BOLD}{title}{Colors.RESET}"
        if source:
            output += f"\n    {Colors.DIM}Source: {source}{Colors.RESET}"
        return output

    @staticmethod
    def sql(query: str) -> str:
        """Format SQL with basic syntax highlighting."""
        # Keywords to highlight
        keywords = [
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER',
            'ON', 'AND', 'OR', 'NOT', 'IN', 'IS', 'NULL', 'AS', 'ORDER', 'BY',
            'GROUP', 'HAVING', 'LIMIT', 'OFFSET', 'INSERT', 'INTO', 'VALUES',
            'UPDATE', 'SET', 'DELETE', 'CREATE', 'TABLE', 'DROP', 'ALTER',
            'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'DISTINCT', 'ASC', 'DESC',
            'UNION', 'INTERSECT', 'EXCEPT', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END'
        ]

        # Format the SQL nicely
        formatted = query.strip()

        # Add newlines for readability
        formatted = re.sub(r'\b(FROM|WHERE|JOIN|LEFT JOIN|RIGHT JOIN|INNER JOIN|ORDER BY|GROUP BY|HAVING|LIMIT)\b',
                          r'\n\1', formatted, flags=re.IGNORECASE)

        # Highlight keywords
        for kw in keywords:
            formatted = re.sub(
                rf'\b({kw})\b',
                f'{Colors.MAGENTA}\\1{Colors.RESET}',
                formatted,
                flags=re.IGNORECASE
            )

        # Indent continuation lines
        lines = formatted.split('\n')
        result = []
        for i, line in enumerate(lines):
            if i == 0:
                result.append(f"    {line.strip()}")
            else:
                result.append(f"      {line.strip()}")

        box_top = f"    {Colors.DIM}┌{'─' * (WIDTH - 8)}┐{Colors.RESET}"
        box_bottom = f"    {Colors.DIM}└{'─' * (WIDTH - 8)}┘{Colors.RESET}"

        return f"{box_top}\n" + '\n'.join(result) + f"\n{box_bottom}"

    @staticmethod
    def text_block(title: str, text: str, icon: str = "•") -> str:
        """Format a text block with wrapping."""
        wrapped = textwrap.fill(text, width=WIDTH - 6, initial_indent="    ", subsequent_indent="    ")
        return f"\n{Colors.GREEN}{icon} {title}:{Colors.RESET}\n{wrapped}"

    @staticmethod
    def table(rows: list[dict], max_rows: int = 20) -> str:
        """Format results as a clean table."""
        if not rows:
            return f"    {Colors.DIM}(no results){Colors.RESET}"

        # Get column names and widths
        columns = list(rows[0].keys())
        col_widths = {}

        for col in columns:
            max_width = len(str(col))
            for row in rows[:max_rows]:
                val_len = len(str(row.get(col, '')))
                max_width = max(max_width, min(val_len, 30))  # Cap at 30 chars
            col_widths[col] = max_width

        # Build the table
        output = []

        # Header
        header_parts = []
        for col in columns:
            header_parts.append(f"{Colors.BOLD}{col:<{col_widths[col]}}{Colors.RESET}")
        header = " │ ".join(header_parts)
        output.append(f"    {header}")

        # Separator
        sep_parts = ["─" * col_widths[col] for col in columns]
        output.append(f"    {'─┼─'.join(sep_parts)}")

        # Rows
        display_rows = rows[:max_rows]
        for row in display_rows:
            row_parts = []
            for col in columns:
                val = str(row.get(col, ''))
                if len(val) > 30:
                    val = val[:27] + "..."
                row_parts.append(f"{val:<{col_widths[col]}}")
            output.append(f"    {' │ '.join(row_parts)}")

        if len(rows) > max_rows:
            output.append(f"    {Colors.DIM}... and {len(rows) - max_rows} more rows{Colors.RESET}")

        output.append(f"\n    {Colors.DIM}({len(rows)} row{'s' if len(rows) != 1 else ''} returned){Colors.RESET}")

        return '\n'.join(output)

    @staticmethod
    def schema_compact(tables: list[dict]) -> str:
        """Format schema in a compact view."""
        output = []
        for table in tables:
            name = table['name']
            cols = table['columns']

            output.append(f"\n    {Colors.BOLD}{name}{Colors.RESET}")
            output.append(f"    {Colors.DIM}{'─' * (len(name) + 4)}{Colors.RESET}")

            for col in cols:
                pk = f"{Colors.YELLOW}PK{Colors.RESET} " if col.get('pk') else "   "
                fk = f" {Colors.CYAN}→ {col['fk']}{Colors.RESET}" if col.get('fk') else ""
                output.append(f"      {pk}{col['name']}: {Colors.DIM}{col['type']}{Colors.RESET}{fk}")

        return '\n'.join(output)

    @staticmethod
    def error(message: str) -> str:
        """Format an error message."""
        return f"\n{Colors.RED}✗ Error: {message}{Colors.RESET}"

    @staticmethod
    def success(message: str) -> str:
        """Format a success message."""
        return f"\n{Colors.GREEN}✓ {message}{Colors.RESET}"

    @staticmethod
    def divider() -> str:
        """Simple divider line."""
        return f"\n{Colors.DIM}{'─' * WIDTH}{Colors.RESET}"


def demo():
    """Demo the formatter."""
    f = Formatter()

    print(f.header("SQL AGENT OUTPUT DEMO"))

    print(f.step(1, "Analyzing Question", "User input"))
    print(f.text_block("Question", "Who are our top 3 customers by total spending?"))

    print(f.step(2, "Generating SQL", "Claude API"))
    print(f.text_block("Reasoning",
        "To find the top 3 customers by total spending, I need to join customers with orders and order_items, "
        "calculate the sum of quantity * unit_price for each customer, then order by total descending and limit to 3."))

    print(f.text_block("Set Theory",
        "This performs a natural join (⨝) of customers, orders, and order_items, "
        "followed by grouping (partition) by customer and aggregation (SUM) on spending."))

    print(f.step(3, "Executing Query", "SQLite database"))
    print(f.sql("SELECT c.name, SUM(oi.quantity * oi.unit_price) as total_spending FROM customers c JOIN orders o ON c.id = o.customer_id JOIN order_items oi ON o.id = oi.order_id GROUP BY c.id, c.name ORDER BY total_spending DESC LIMIT 3"))

    print(f.step(4, "Results", "Query execution"))
    results = [
        {"name": "Carol Williams", "total_spending": 6518.73},
        {"name": "Eva Martinez", "total_spending": 3953.79},
        {"name": "Alice Johnson", "total_spending": 3502.85},
    ]
    print(f.table(results))

    print(f.success("Query completed successfully"))


if __name__ == "__main__":
    demo()
