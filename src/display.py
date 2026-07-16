"""Plain-text table formatting for query results."""


def format_table(columns, rows):
    """Render *columns* and *rows* as an aligned text table.

    Returns a friendly message instead of an empty table when there
    are no rows. NULL values are shown as ``-``.
    """
    if not rows:
        return "No results found."
    cells = [
        ["-" if value is None else str(value) for value in row]
        for row in rows
    ]
    headers = [str(column) for column in columns]
    widths = [
        max(len(headers[i]), *(len(row[i]) for row in cells))
        for i in range(len(headers))
    ]
    header_line = " | ".join(
        header.ljust(width) for header, width in zip(headers, widths)
    )
    separator = "-+-".join("-" * width for width in widths)
    body_lines = [
        " | ".join(
            value.ljust(width) for value, width in zip(row, widths)
        )
        for row in cells
    ]
    row_count = len(rows)
    plural = "s" if row_count != 1 else ""
    footer = f"({row_count} row{plural})"
    return "\n".join([header_line, separator, *body_lines, footer])
