"""Build parameterised SELECT statements for the GUI query builder.

Identifiers (tables, columns) are only ever taken from the whitelist
in schema_meta.py; everything the user types is returned as a bound
parameter, never spliced into the SQL text. The module has no tkinter
dependency so the generation logic can be unit-tested headlessly.
"""

# operator name -> (SQL clause template, parameter transform)
OPERATORS = {
    "=": ("{column} = ?", lambda value: value),
    "!=": ("{column} <> ?", lambda value: value),
    ">": ("{column} > ?", lambda value: value),
    ">=": ("{column} >= ?", lambda value: value),
    "<": ("{column} < ?", lambda value: value),
    "<=": ("{column} <= ?", lambda value: value),
    "contains": (
        "LOWER({column}) LIKE LOWER(?)",
        lambda value: f"%{value}%",
    ),
    "starts with": (
        "LOWER({column}) LIKE LOWER(?)",
        lambda value: f"{value}%",
    ),
}

OPERATOR_NAMES = tuple(OPERATORS)
COMBINATORS = ("AND", "OR")


def build_select(source, columns, conditions=(), combinator="AND",
                 order_by=None, descending=False, limit=None):
    """Return ``(sql, params)`` for the described query.

    * *source* -- a source dict from :mod:`schema_meta`.
    * *columns* -- aliases to include in the SELECT list.
    * *conditions* -- iterable of ``(alias, operator, value)``.
    * *combinator* -- ``"AND"`` or ``"OR"`` between conditions.
    * *order_by* -- optional alias to sort by (*descending* flips it).
    * *limit* -- optional maximum number of rows.

    Raises :class:`ValueError` for anything outside the whitelist so
    the GUI can show a friendly message.
    """
    column_map = dict(source["columns"])
    if not columns:
        raise ValueError("Select at least one column.")
    unknown = [alias for alias in columns if alias not in column_map]
    if unknown:
        raise ValueError(f"Unknown column(s): {', '.join(unknown)}")
    if combinator not in COMBINATORS:
        raise ValueError(f"Unknown combinator: {combinator}")

    select_list = ",\n       ".join(
        f"{column_map[alias]} AS {alias}" for alias in columns
    )
    lines = [f"SELECT {select_list}", f"FROM {source['from_clause']}"]

    params = []
    clauses = []
    for alias, operator, value in conditions:
        if alias not in column_map:
            raise ValueError(f"Unknown filter column: {alias}")
        if operator not in OPERATORS:
            raise ValueError(f"Unknown operator: {operator}")
        template, transform = OPERATORS[operator]
        clauses.append(template.format(column=column_map[alias]))
        params.append(transform(value))
    if clauses:
        lines.append("WHERE " + f" {combinator} ".join(clauses))

    if order_by:
        if order_by not in column_map:
            raise ValueError(f"Unknown sort column: {order_by}")
        direction = " DESC" if descending else ""
        lines.append(f"ORDER BY {column_map[order_by]}{direction}")

    if limit is not None:
        lines.append(f"LIMIT {int(limit)}")

    return "\n".join(lines), tuple(params)
