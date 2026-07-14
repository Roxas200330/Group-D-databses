"""Tkinter GUI for the university record system.

Offers the standard reports, plus a
Query Builder tab where users compose their own SELECT queries from
whitelisted tables, columns, filters and sorting. The generated SQL
is shown for transparency and always uses bound parameters.

Run from the repository root:

    python3 src/gui.py

Uses only the Python standard library (tkinter), so it works with the
zero-setup SQLite back end as well as MySQL.
"""

import sys

try:
    import tkinter as tk
    from tkinter import messagebox, ttk
except ImportError:
    print(
        "tkinter is not available in this Python installation."
    )
    sys.exit(1)

import db
import queries
import querybuilder
import schema_meta

PAD = {"padx": 8, "pady": 4}


def _column_width(header, rows, index):
    longest = len(str(header))
    for row in rows:
        value = row[index]
        if value is not None:
            longest = max(longest, len(str(value)))
    return max(80, min(340, longest * 8))


class ResultsPane(ttk.LabelFrame):
    """Scrollable table of query results, shared by both tabs."""

    def __init__(self, parent):
        super().__init__(parent, text="Results")
        self.tree = ttk.Treeview(self, show="headings", height=12)
        y_scroll = ttk.Scrollbar(
            self, orient="vertical", command=self.tree.yview
        )
        x_scroll = ttk.Scrollbar(
            self, orient="horizontal", command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set
        )
        self.status = ttk.Label(self, text="Run a query to see results.")
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        self.status.grid(row=2, column=0, columnspan=2, sticky="w")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def show(self, columns, rows):
        """Replace the table contents with a new result set."""
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(columns)
        for index, name in enumerate(columns):
            self.tree.heading(name, text=name)
            width = _column_width(name, rows, index)
            self.tree.column(name, width=width, stretch=True)
        for row in rows:
            values = ["-" if v is None else v for v in row]
            self.tree.insert("", "end", values=values)
        count = len(rows)
        plural = "s" if count != 1 else ""
        text = f"{count} row{plural}."
        if count == 0:
            text = "No results found."
        self.status.configure(text=text)


class StandardTab(ttk.Frame):
    """The predefined reports from queries.CATALOGUE."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.entries = []
        self.current = 0
        self.listbox = tk.Listbox(
            self, height=len(queries.CATALOGUE), width=55,
            exportselection=False,
        )
        for entry in queries.CATALOGUE:
            self.listbox.insert("end", entry["title"])
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        self.params_frame = ttk.LabelFrame(self, text="Parameters")
        run_button = ttk.Button(
            self, text="Run query", command=self._run
        )
        self.listbox.grid(row=0, column=0, rowspan=2, sticky="nsew",
                          **PAD)
        self.params_frame.grid(row=0, column=1, sticky="new", **PAD)
        run_button.grid(row=1, column=1, sticky="ne", **PAD)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.listbox.selection_set(0)
        self._on_select()

    def _on_select(self, _event=None):
        """Rebuild the parameter fields for the selected query."""
        selection = self.listbox.curselection()
        if selection:
            self.current = selection[0]
        for child in self.params_frame.winfo_children():
            child.destroy()
        self.entries = []
        entry_specs = queries.CATALOGUE[self.current]["params"]
        for row, (prompt, converter) in enumerate(entry_specs):
            label = ttk.Label(self.params_frame, text=prompt + ":")
            field = ttk.Entry(self.params_frame, width=34)
            label.grid(row=row, column=0, sticky="w", **PAD)
            field.grid(row=row, column=1, sticky="ew", **PAD)
            self.entries.append((prompt, converter, field))
        self.params_frame.columnconfigure(1, weight=1)

    def _run(self):
        """Validate parameters, run the query, show the results."""
        entry = queries.CATALOGUE[self.current]
        values = []
        for prompt, converter, field in self.entries:
            raw = field.get().strip()
            if not raw:
                messagebox.showwarning(
                    "Missing input", f"Please fill in: {prompt}"
                )
                return
            try:
                values.append(converter(raw))
            except ValueError:
                messagebox.showerror(
                    "Invalid input",
                    f"'{raw}' is not a valid {converter.__name__} "
                    f"for: {prompt}",
                )
                return
        try:
            columns, rows = entry["runner"](self.app.database, *values)
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc))
            return
        except Exception as exc:  # pragma: no cover - driver errors
            messagebox.showerror("Query failed", str(exc))
            return
        self.app.show_results(columns, rows)


class BuilderTab(ttk.Frame):
    """Visual builder for user-composed SELECT queries."""

    MAX_CONDITIONS = 3

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        left = ttk.Frame(self)
        right = ttk.Frame(self)
        left.grid(row=0, column=0, sticky="nsew", **PAD)
        right.grid(row=0, column=1, sticky="nsew", **PAD)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        ttk.Label(left, text="Data source:").grid(
            row=0, column=0, sticky="w", **PAD
        )
        self.source_var = tk.StringVar(
            value=schema_meta.SOURCE_NAMES[0]
        )
        source_box = ttk.Combobox(
            left, textvariable=self.source_var, state="readonly",
            values=schema_meta.SOURCE_NAMES, width=36,
        )
        source_box.grid(row=0, column=1, sticky="ew", **PAD)
        source_box.bind("<<ComboboxSelected>>", self._on_source_change)

        ttk.Label(left, text="Columns (Cmd/Ctrl-click):").grid(
            row=1, column=0, sticky="nw", **PAD
        )
        self.columns_list = tk.Listbox(
            left, selectmode="extended", height=9, width=30,
            exportselection=False,
        )
        self.columns_list.grid(row=1, column=1, sticky="nsew", **PAD)
        left.columnconfigure(1, weight=1)

        preview_frame = ttk.LabelFrame(left, text="Generated SQL")
        preview_frame.grid(
            row=2, column=0, columnspan=2, sticky="nsew", **PAD
        )
        self.preview = tk.Text(
            preview_frame, height=8, width=48, state="disabled",
            font="TkFixedFont",
        )
        self.preview.pack(fill="both", expand=True, padx=4, pady=4)

        filters = ttk.LabelFrame(right, text="Filters (optional)")
        filters.grid(row=0, column=0, sticky="new", **PAD)
        self.conditions = []
        for row in range(self.MAX_CONDITIONS):
            column_box = ttk.Combobox(
                filters, state="readonly", width=20
            )
            operator_box = ttk.Combobox(
                filters, state="readonly", width=10,
                values=querybuilder.OPERATOR_NAMES,
            )
            operator_box.set("=")
            value_field = ttk.Entry(filters, width=18)
            column_box.grid(row=row, column=0, sticky="w", **PAD)
            operator_box.grid(row=row, column=1, sticky="w", **PAD)
            value_field.grid(row=row, column=2, sticky="ew", **PAD)
            self.conditions.append(
                (column_box, operator_box, value_field)
            )
        filters.columnconfigure(2, weight=1)
        self.combinator_var = tk.StringVar(value="AND")
        combine = ttk.Frame(filters)
        combine.grid(
            row=self.MAX_CONDITIONS, column=0, columnspan=3,
            sticky="w",
        )
        ttk.Label(combine, text="Combine filters with:").pack(
            side="left", **PAD
        )
        for name in querybuilder.COMBINATORS:
            ttk.Radiobutton(
                combine, text=name, value=name,
                variable=self.combinator_var,
            ).pack(side="left", **PAD)

        sorting = ttk.LabelFrame(right, text="Sorting and limit")
        sorting.grid(row=1, column=0, sticky="new", **PAD)
        ttk.Label(sorting, text="Sort by:").grid(
            row=0, column=0, sticky="w", **PAD
        )
        self.order_box = ttk.Combobox(
            sorting, state="readonly", width=20
        )
        self.order_box.grid(row=0, column=1, sticky="w", **PAD)
        self.descending_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            sorting, text="Descending", variable=self.descending_var
        ).grid(row=0, column=2, sticky="w", **PAD)
        ttk.Label(sorting, text="Row limit (blank = all):").grid(
            row=1, column=0, sticky="w", **PAD
        )
        self.limit_field = ttk.Entry(sorting, width=8)
        self.limit_field.grid(row=1, column=1, sticky="w", **PAD)

        ttk.Button(
            right, text="Run custom query", command=self._run
        ).grid(row=2, column=0, sticky="e", **PAD)
        right.columnconfigure(0, weight=1)

        self._on_source_change()

    def _on_source_change(self, _event=None):
        """Refresh column choices when the data source changes."""
        source = schema_meta.get_source(self.source_var.get())
        aliases = [alias for alias, _expr in source["columns"]]
        self.columns_list.delete(0, "end")
        for alias in aliases:
            self.columns_list.insert("end", alias)
        self.columns_list.selection_set(0, "end")
        for column_box, operator_box, value_field in self.conditions:
            column_box.configure(values=[""] + aliases)
            column_box.set("")
            operator_box.set("=")
            value_field.delete(0, "end")
        self.order_box.configure(values=[""] + aliases)
        self.order_box.set("")

    def _gather_conditions(self):
        """Collect the filled-in filter rows as builder conditions."""
        gathered = []
        for column_box, operator_box, value_field in self.conditions:
            alias = column_box.get().strip()
            value = value_field.get().strip()
            if alias and value:
                gathered.append((alias, operator_box.get(), value))
        return gathered

    def _set_preview(self, text):
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", text)
        self.preview.configure(state="disabled")

    def _run(self):
        """Build the SELECT, run it and display SQL + results."""
        source = schema_meta.get_source(self.source_var.get())
        selected = [
            self.columns_list.get(i)
            for i in self.columns_list.curselection()
        ]
        limit_text = self.limit_field.get().strip()
        limit = None
        if limit_text:
            try:
                limit = int(limit_text)
            except ValueError:
                messagebox.showerror(
                    "Invalid input",
                    "Row limit must be a whole number.",
                )
                return
        try:
            sql, params = querybuilder.build_select(
                source,
                selected,
                conditions=self._gather_conditions(),
                combinator=self.combinator_var.get(),
                order_by=self.order_box.get() or None,
                descending=self.descending_var.get(),
                limit=limit,
            )
        except ValueError as exc:
            messagebox.showerror("Cannot build query", str(exc))
            return
        try:
            columns, rows = self.app.database.run(sql, params)
        except Exception as exc:  # pragma: no cover - driver errors
            messagebox.showerror("Query failed", str(exc))
            return
        preview = sql
        if params:
            preview += f"\n\n-- parameters: {params!r}"
        self._set_preview(preview)
        self.app.show_results(columns, rows)


class App(tk.Tk):
    """Main window: notebook of query tabs above a results table."""

    def __init__(self, database):
        super().__init__()
        self.database = database
        self.title("University Record Management System")
        self.geometry("1100x780")
        self.minsize(900, 600)
        notebook = ttk.Notebook(self)
        self.standard_tab = StandardTab(notebook, self)
        self.builder_tab = BuilderTab(notebook, self)
        notebook.add(self.standard_tab, text="Standard queries")
        notebook.add(self.builder_tab, text="Query builder")
        self.results = ResultsPane(self)
        backend_label = ttk.Label(
            self, text=f"Back end: {database.backend}"
        )
        notebook.pack(side="top", fill="x", padx=8, pady=6)
        backend_label.pack(side="bottom", anchor="w", padx=8, pady=2)
        self.results.pack(
            side="top", fill="both", expand=True, padx=8, pady=6
        )
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def show_results(self, columns, rows):
        """Display a result set in the shared results pane."""
        self.results.show(columns, rows)

    def _on_close(self):
        self.database.close()
        self.destroy()


def main():
    """Connect to the database and start the GUI."""
    try:
        database = db.connect()
    except db.DatabaseError as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Connection error", str(exc))
        root.destroy()
        return 1
    app = App(database)
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
