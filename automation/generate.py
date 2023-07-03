import argparse
from typing import List

import pandas as pd

from pandas.core.series import Series

TOPIC_COLUMN_NAME = "topic"
DIFFICULTY_COLUMN_NAME = "difficulty"
PRICE_COLUMN_NAME = "price"
RELEASE_YEAR_COLUMN_NAME = "release_year"
URL_COLUMN_NAME = "url"
LABEL_COLUMN_NAME = "label"
AUTHOR_COLUMN_NAME = "author"
FORMAT_COLUMN_NAME = "format"

AUTOGENERATED_COURSES_TABLE_TOKEN = "<!--- AUTOGENERATED_COURSES_TABLE -->"

WARNING_HEADER = [
    "<!---",
    "   WARNING: DO NOT EDIT THIS TABLE MANUALLY. IT IS AUTOMATICALLY GENERATED.",
    "   HEAD OVER TO CONTRIBUTING.MD FOR MORE DETAILS ON HOW TO MAKE CHANGES PROPERLY.",
    "-->"
]

TABLE_HEADER = [
    "| **topic** | **format** | **difficulty** | **release year** | **price** | **course** |",
    "|:---------:|:----------:|:--------------:|:----------------:|:---------:|:----------:|"
]

DIFFICULTY_MAP = {
    1: "🟩⬜⬜",
    2: "🟩🟩⬜",
    3: "🟩🟩🟩"
}


def read_lines_from_file(path: str) -> List[str]:
    with open(path) as file:
        return [line.rstrip() for line in file]


def save_lines_to_file(path: str, lines: List[str]) -> None:
    with open(path, "w") as f:
        for line in lines:
            f.write("%s\n" % line)


def format_entry(entry: Series) -> str:
    topic = entry.loc[TOPIC_COLUMN_NAME]
    difficulty = DIFFICULTY_MAP[entry.loc[DIFFICULTY_COLUMN_NAME]]
    release_year = entry.loc[RELEASE_YEAR_COLUMN_NAME]
    price = entry.loc[PRICE_COLUMN_NAME]
    format = entry.loc[FORMAT_COLUMN_NAME]
    url = entry.loc[URL_COLUMN_NAME]
    label = entry.loc[LABEL_COLUMN_NAME]
    author = entry.loc[AUTHOR_COLUMN_NAME]
    return f"| {topic} | {format} | {difficulty} | {release_year} | {price} | [{label}]({url}) by {author} |"


def load_table_entries(path: str) -> List[str]:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return [
        format_entry(row)
        for _, row
        in df.iterrows()
    ]


def search_lines_with_token(lines: List[str], token: str) -> List[int]:
    result = []
    for line_index, line in enumerate(lines):
        if token in line:
            result.append(line_index)
    return result


def inject_markdown_table_into_readme(readme_lines: List[str], table_lines: List[str]) -> List[str]:
    lines_with_token_indexes = search_lines_with_token(lines=readme_lines, token=AUTOGENERATED_COURSES_TABLE_TOKEN)
    if len(lines_with_token_indexes) != 2:
        raise Exception(f"Please inject two {AUTOGENERATED_COURSES_TABLE_TOKEN} "
                        f"tokens to signal start and end of autogenerated table.")

    [table_start_line_index, table_end_line_index] = lines_with_token_indexes
    return readme_lines[:table_start_line_index + 1] + table_lines + readme_lines[table_end_line_index:]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data_path', default='automation/data.csv')
    parser.add_argument('-r', '--readme_path', default='README.md')
    args = parser.parse_args()

    table_lines = load_table_entries(path=args.data_path)
    table_lines = WARNING_HEADER + TABLE_HEADER + table_lines
    readme_lines = read_lines_from_file(path=args.readme_path)
    readme_lines = inject_markdown_table_into_readme(readme_lines=readme_lines, table_lines=table_lines)
    save_lines_to_file(path=args.readme_path, lines=readme_lines)
