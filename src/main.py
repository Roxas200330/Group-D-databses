"""University record management system -- command-line interface.

Group D end-of-module assignment.
Presents a numbered menu of reports; each option prompts for its
parameters, executes a parameterised SQL query through the query
engine (queries.py) and prints the results as a text table.

Run from the repository root:

    python3 src/main.py

By default this uses the zero-setup SQLite back end (the database is
created and seeded on first run). To use the team's MySQL database,
copy config.ini.example to config.ini and set backend = mysql.
"""

import sys

import db
import display
import queries

BANNER = """
==============================================
  University Record Management System
  Group D - Databases and Information Systems
==============================================
""".rstrip()


def show_menu():
    """Print the numbered list of available queries."""
    print("\nAvailable queries:")
    for number, entry in enumerate(queries.CATALOGUE, start=1):
        print(f"  {number}. {entry['title']}")
    print("  0. Exit")


def prompt_parameters(param_specs, database):
    """Collect one value per (prompt, converter, options) spec.

    Entering ``?`` lists the valid values for parameters that have an
    option provider; values entered earlier narrow the listing where
    a cascading provider supports it (e.g. lecturers for the course
    already chosen). Re-prompts on invalid numeric input. Returns
    None if the user aborts with an empty line.
    """
    values = []
    context = {}
    for prompt, converter, options in param_specs:
        while True:
            raw = input(f"{prompt}: ").strip()
            if not raw:
                print("Cancelled (empty input).")
                return None
            if raw == "?" and options is not None:
                listing = ", ".join(options(database, context))
                print("Options: " + listing)
                continue
            try:
                values.append(converter(raw))
            except ValueError:
                print(f"Please enter a valid {converter.__name__}.")
                continue
            context[prompt] = raw
            break
    return values


def run_choice(database, entry):
    """Prompt for an entry's parameters, run it and print results."""
    print(f"\n--- {entry['title']} ---")
    if any(options for _p, _c, options in entry["params"]):
        print("(enter ? to list valid values)")
    values = prompt_parameters(entry["params"], database)
    if values is None:
        return
    try:
        columns, rows = entry["runner"](database, *values)
    except ValueError as exc:
        print(f"Error: {exc}")
        return
    print()
    print(display.format_table(columns, rows))


def main():
    """Connect to the database and run the interactive menu loop."""
    print(BANNER)
    try:
        database = db.connect()
    except db.DatabaseError as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Connected using the {database.backend} back end.")
    try:
        while True:
            show_menu()
            choice = input("\nSelect an option: ").strip()
            if choice == "0":
                print("Goodbye.")
                break
            if not choice.isdigit() or not (
                1 <= int(choice) <= len(queries.CATALOGUE)
            ):
                print(
                    "Please enter a number between 0 and "
                    f"{len(queries.CATALOGUE)}."
                )
                continue
            run_choice(database, queries.CATALOGUE[int(choice) - 1])
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye.")
    finally:
        database.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
