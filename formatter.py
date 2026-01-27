"""
Output Formatter for SQL Agent.

Provides clean, structured terminal output with:
- Box drawing for sections
- Formatted tables for results
- Syntax highlighting for SQL
- Clean JSON display
- Animated spinners for wait states
"""

import re
import sys
import textwrap
import threading
import time
from typing import Any
from contextlib import contextmanager


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
    def _format_value(val: Any, width: int) -> str:
        """Format a value for display with proper alignment and formatting."""
        if val is None:
            return f"{Colors.DIM}{'NULL':^{width}}{Colors.RESET}"

        # Format numbers nicely
        if isinstance(val, float):
            # Check if it looks like currency (2 decimal places make sense)
            if abs(val) >= 1000:
                formatted = f"{val:,.2f}"
            else:
                formatted = f"{val:.2f}"
            # Right-align numbers
            if len(formatted) > width:
                formatted = formatted[:width-3] + "..."
            return f"{formatted:>{width}}"
        elif isinstance(val, int):
            formatted = f"{val:,}"
            if len(formatted) > width:
                formatted = formatted[:width-3] + "..."
            return f"{formatted:>{width}}"
        else:
            # String value - left align
            s = str(val)
            if len(s) > width:
                s = s[:width-3] + "..."
            return f"{s:<{width}}"

    @staticmethod
    def table(rows: list[dict], max_rows: int = 20) -> str:
        """Format results as a clean boxed table."""
        if not rows:
            box_width = 30
            return (
                f"\n    {Colors.DIM}╭{'─' * box_width}╮{Colors.RESET}\n"
                f"    {Colors.DIM}│{Colors.RESET}{'No results':^{box_width}}{Colors.DIM}│{Colors.RESET}\n"
                f"    {Colors.DIM}╰{'─' * box_width}╯{Colors.RESET}"
            )

        # Get column names and widths
        columns = list(rows[0].keys())
        col_widths = {}

        for col in columns:
            max_width = len(str(col))
            for row in rows[:max_rows]:
                val = row.get(col, '')
                # Format value to get actual display width
                if isinstance(val, float):
                    val_str = f"{val:,.2f}" if abs(val) >= 1000 else f"{val:.2f}"
                elif isinstance(val, int):
                    val_str = f"{val:,}"
                else:
                    val_str = str(val) if val is not None else "NULL"
                max_width = max(max_width, min(len(val_str), 30))
            col_widths[col] = max_width

        # Calculate total table width
        content_width = sum(col_widths.values()) + (len(columns) - 1) * 3  # 3 for " │ "

        output = []

        # Top border
        output.append(f"    {Colors.DIM}╭{'─' * (content_width + 2)}╮{Colors.RESET}")

        # Header row
        header_parts = []
        for col in columns:
            # Center and bold the header
            header_parts.append(f"{Colors.BOLD}{Colors.CYAN}{col:^{col_widths[col]}}{Colors.RESET}")
        header = " │ ".join(header_parts)
        output.append(f"    {Colors.DIM}│{Colors.RESET} {header} {Colors.DIM}│{Colors.RESET}")

        # Header separator
        sep_parts = ["─" * col_widths[col] for col in columns]
        output.append(f"    {Colors.DIM}├{'─┼─'.join(sep_parts)}──┤{Colors.RESET}")

        # Data rows
        display_rows = rows[:max_rows]
        for i, row in enumerate(display_rows):
            row_parts = []
            for col in columns:
                val = row.get(col)
                formatted = Formatter._format_value(val, col_widths[col])
                row_parts.append(formatted)
            row_str = " │ ".join(row_parts)
            output.append(f"    {Colors.DIM}│{Colors.RESET} {row_str} {Colors.DIM}│{Colors.RESET}")

        # Bottom border
        output.append(f"    {Colors.DIM}╰{'─' * (content_width + 2)}╯{Colors.RESET}")

        # Summary line
        if len(rows) > max_rows:
            summary = f"{len(rows):,} rows ({max_rows} shown)"
        else:
            summary = f"{len(rows):,} row{'s' if len(rows) != 1 else ''}"
        output.append(f"    {Colors.DIM}{summary}{Colors.RESET}")

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


class Spinner:
    """Animated spinner for long-running operations."""

    # Themed animation sets
    THEMES = {
        "thinking": {
            "frames": [
                "    ( o.o)  thinking...  ",
                "    (o. o)  thinking..   ",
                "    ( o.o)  thinking.    ",
                "    (o. o)  thinking     ",
                "    ( o.o)  thinking.    ",
                "    (o. o)  thinking..   ",
            ],
            "done": "    ( ^.^)  got it!",
        },
        "querying": {
            "frames": [
                "    [>    ]  querying db  ",
                "    [=>   ]  querying db  ",
                "    [==>  ]  querying db  ",
                "    [ ==> ]  querying db  ",
                "    [  ==>]  querying db  ",
                "    [   =>]  querying db  ",
                "    [    >]  querying db  ",
                "    [   <=]  querying db  ",
                "    [  <==]  querying db  ",
                "    [ <== ]  querying db  ",
                "    [<==  ]  querying db  ",
                "    [<=   ]  querying db  ",
            ],
            "done": "    [=====]  done!",
        },
        "writing": {
            "frames": [
                "    /  writing sql       ",
                "    /  writing sql.      ",
                "    |  writing sql..     ",
                "    |  writing sql...    ",
                "    \\  writing sql....   ",
                "    \\  writing sql.....  ",
                "    |  writing sql...... ",
                "    |  writing sql.......",
            ],
            "done": "    *  sql ready!",
        },
        "reading": {
            "frames": [
                "    ~(=^.^)  reading results      ",
                "    ~(=^.^)>  reading results     ",
                "    ~(=^.^)>>  reading results    ",
                "    ~(=^.^)>>>  reading results   ",
                "     ~(=^.^)>>>  reading results  ",
                "      ~(=^.^)>>>  reading results ",
                "       ~(=^.^)>>>  reading results",
                "      ~(=^.^)>>>  reading results ",
                "     ~(=^.^)>>>  reading results  ",
                "    ~(=^.^)>>>  reading results   ",
                "    ~(=^.^)>>  reading results    ",
                "    ~(=^.^)>  reading results     ",
            ],
            "done": "    ~(=^.^)  all done!",
        },
    }

    def __init__(self, theme: str = "thinking", speed: float = 0.12):
        self.theme = self.THEMES.get(theme, self.THEMES["thinking"])
        self.speed = speed
        self._stop_event = threading.Event()
        self._thread = None

    def _animate(self):
        """Run the animation loop in a background thread."""
        frames = self.theme["frames"]
        i = 0
        while not self._stop_event.is_set():
            frame = frames[i % len(frames)]
            sys.stdout.write(f"\r{Colors.CYAN}{frame}{Colors.RESET}")
            sys.stdout.flush()
            i += 1
            self._stop_event.wait(self.speed)
        # Clear the spinner line and show done message
        sys.stdout.write(f"\r{' ' * (WIDTH)}\r")
        sys.stdout.flush()

    def start(self):
        """Start the spinner animation."""
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self, show_done: bool = False):
        """Stop the spinner animation."""
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        if show_done:
            done_msg = self.theme["done"]
            sys.stdout.write(f"\r{Colors.GREEN}{done_msg}{Colors.RESET}\n")
            sys.stdout.flush()


@contextmanager
def spinner(theme: str = "thinking", show_done: bool = False):
    """Context manager for easy spinner usage.

    Usage:
        with spinner("thinking"):
            slow_operation()
    """
    s = Spinner(theme=theme)
    s.start()
    try:
        yield s
    finally:
        s.stop(show_done=show_done)


def demo():
    """Demo the formatter."""
    f = Formatter()

    print(f.header("SQL AGENT OUTPUT DEMO"))

    # Spinner demos
    print(f.step(0, "Spinner Demos", ""))
    for theme in ["thinking", "writing", "reading", "querying"]:
        with spinner(theme, show_done=True):
            time.sleep(2.5)

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
    print(f.success("Query completed"))

    # Demo empty results
    print(f.step(5, "Empty Results Demo", ""))
    print(f.table([]))

    # Demo with larger numbers
    print(f.step(6, "Large Numbers Demo", ""))
    large_results = [
        {"product": "Widget Pro", "units_sold": 12345, "revenue": 1234567.89},
        {"product": "Gadget Plus", "units_sold": 9876, "revenue": 987654.32},
    ]
    print(f.table(large_results))


if __name__ == "__main__":
    demo()
