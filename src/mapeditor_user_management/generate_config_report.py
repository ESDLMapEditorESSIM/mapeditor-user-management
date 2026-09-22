import argparse
import json
import os

from dotenv import load_dotenv

from mapeditor_user_management.mongo_interface import MongoInterface


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="MapEditor Config Report",
        description=(
            "Generate a markdown report comparing a list-of-dicts user setting "
            "across all users, deduplicating entries into numbered versions."
        ),
    )
    parser.add_argument(
        "config_name",
        nargs="?",
        default=os.environ.get("REPORT_CONFIG_NAME"),
        help="Name of the user setting to inspect, e.g. 'esdl_services'",
    )
    parser.add_argument(
        "identifier",
        nargs="?",
        default=os.environ.get("REPORT_IDENTIFIER", "name"),
        help="Key within each list entry used to identify/group entries (default: 'name')",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=os.environ.get("REPORT_OUTPUT_FILE"),
        help="Output markdown file path",
    )
    parser.add_argument("-mh", "--mongo-host", default=os.environ.get("MONGO_HOST"))
    parser.add_argument("-mp", "--mongo-port", default=os.environ.get("MONGO_PORT"))
    args = parser.parse_args()
    if not args.config_name:
        raise IOError(
            "A 'config_name' must be supplied as the first argument or as 'REPORT_CONFIG_NAME' ENV VAR."
        )
    return args


def build_report(config_name: str, identifier: str, users: list[dict]):
    columns = []  # entry identifier values, in order of first appearance
    versions: dict[
        str, list[dict]
    ] = {}  # identifier value -> list of unique entry dicts
    counts: dict[str, list[int]] = {}  # identifier value -> occurrence count per entry
    table: dict[
        str, dict[str, int]
    ] = {}  # user name -> {identifier value: version number}

    for user in users:
        user_name = user.get("name")
        table.setdefault(user_name, {})

        entries = user.get(config_name)
        if not isinstance(entries, list):
            continue

        for entry in entries:
            if not isinstance(entry, dict) or identifier not in entry:
                continue
            entry_id = entry[identifier]
            if entry_id not in columns:
                columns.append(entry_id)

            entry_versions = versions.setdefault(entry_id, [])
            entry_counts = counts.setdefault(entry_id, [])
            index = next(
                (i for i, existing in enumerate(entry_versions) if existing == entry),
                None,
            )
            if index is None:
                entry_versions.append(entry)
                entry_counts.append(0)
                index = len(entry_versions) - 1

            entry_counts[index] += 1
            table[user_name][entry_id] = index

    # renumber versions so _1 is the most common, _2 the next most common, etc.
    for entry_id in columns:
        entry_versions = versions[entry_id]
        entry_counts = counts[entry_id]
        order = sorted(range(len(entry_versions)), key=lambda i: -entry_counts[i])
        old_to_new = {old_index: new_index for new_index, old_index in enumerate(order)}
        versions[entry_id] = [entry_versions[old_index] for old_index in order]
        for user_table in table.values():
            if entry_id in user_table:
                user_table[entry_id] = old_to_new[user_table[entry_id]] + 1

    return columns, versions, table


def render_markdown(
    config_name: str,
    identifier: str,
    mongo_host: str,
    mongo_port: str,
    columns: list[str],
    versions: dict[str, list[dict]],
    table: dict[str, dict[str, int]],
) -> str:
    lines = [
        f"# Config report: `{config_name}` (identifier: `{identifier}`)",
        "",
        f"Mongo: `{mongo_host}:{mongo_port}`",
        "",
        "Table cells hold the version number of that entry for the user (empty if the "
        "user does not have it). Version `_1` is the most common variant found across "
        "all users, `_2` is the next most common, and so on; see the collapsible "
        "sections below the table for each version's content.",
        "",
    ]

    lines.append("| user | " + " | ".join(columns) + " |")
    lines.append("| --- | " + " | ".join(["---"] * len(columns)) + " |")
    for user_name in sorted(table.keys(), key=lambda name: (name is None, name)):
        row = [str(table[user_name].get(column, "")) for column in columns]
        lines.append(f"| {user_name} | " + " | ".join(row) + " |")
    lines.append("")

    for column in columns:
        for i, entry in enumerate(versions[column]):
            lines.append("<details>")
            lines.append(f"<summary>{column}_{i + 1}</summary>")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(entry, indent=2, ensure_ascii=False))
            lines.append("```")
            lines.append("")
            lines.append("</details>")
            lines.append("")

    return "\n".join(lines)


def main():
    args = parse_args()

    output_path = args.output or f"reports/{args.config_name}_report.md"
    if os.path.exists(output_path):
        raise IOError(
            f"Report already exists at '{output_path}', refusing to overwrite"
        )

    mongo_interface = MongoInterface(args.mongo_host, args.mongo_port)
    users = list(mongo_interface.get_all_users())

    columns, versions, table = build_report(args.config_name, args.identifier, users)
    markdown = render_markdown(
        args.config_name,
        args.identifier,
        args.mongo_host,
        args.mongo_port,
        columns,
        versions,
        table,
    )

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as open_file:
        open_file.write(markdown)

    print(f"Wrote report to '{output_path}'")


if __name__ == "__main__":
    load_dotenv()
    main()
