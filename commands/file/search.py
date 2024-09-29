import os
import rich
import typer

import re
import glob
from typing import List, Union


class SearchCondition:
    def __init__(self, pattern: str, negate: bool = False):
        self.pattern = pattern
        self.negate = negate

    def match(self, text: str) -> bool:
        result = re.search(self.pattern, text)
        return not result if self.negate else bool(result)

    def __and__(self, other):
        return SearchQuery().add(self).add(other)

    def __or__(self, other):
        return SearchQuery().add(self).add(other).OR()

    def __invert__(self):
        return SearchCondition(self.pattern, not self.negate)


class SearchQuery:
    def __init__(self):
        self.conditions: List[Union[SearchCondition, "SearchQuery"]] = []
        self.operator: str = "AND"

    def add(self, condition: Union[SearchCondition, "SearchQuery"]):
        self.conditions.append(condition)
        return self

    def OR(self):
        self.operator = "OR"
        return self

    def AND(self):
        self.operator = "AND"
        return self

    def match(self, text: str) -> bool:
        if self.operator == "AND":
            return all(condition.match(text) for condition in self.conditions)
        elif self.operator == "OR":
            return any(condition.match(text) for condition in self.conditions)

    def __and__(self, other):
        return SearchQuery().add(self).add(other)

    def __or__(self, other):
        return SearchQuery().add(self).add(other).OR()

    def __invert__(self):
        inverted = SearchQuery()
        for condition in self.conditions:
            inverted.add(~condition)
        inverted.operator = "OR" if self.operator == "AND" else "AND"
        return inverted


def search_files(
    glob_pattern: str, query: Union[SearchCondition, SearchQuery]
) -> List[str]:
    matching_files = []
    for file_path in glob.glob(glob_pattern, recursive=True):
        # check if the file is a directory
        if os.path.isdir(file_path):
            continue

        # typer.echo(f"Searching in file: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                if query.match(content):
                    matching_files.append(file_path)
        except Exception as e:
            pass
    return matching_files


# Helper functions to create conditions
def contains(pattern: str) -> SearchCondition:
    return SearchCondition(pattern)


def not_contains(pattern: str) -> SearchCondition:
    return ~SearchCondition(pattern)


# Example usage
"""
if __name__ == "__main__":
    files_to_search = "apps/mm10/src/cards/**/*.tsx"  # Searches all .py files in current directory and

    # Even more complex query
    query = contains("<CardPage") & (
        contains(r"image") | contains("src:") & contains("const img = ")
    )
    print(search_files(files_to_search, query))
"""

"""
"""


def search(pattern: str, condition: str):
    """
    Example:
    lullu_cli file search "apps/mm10/src/cards/**/*.tsx" "<CardPage" "image" "src:" "const img = "
    """

    files_to_search = pattern  # Searches all .py files in current directory and

    # Even more complex query
    query = contains("")
    for condition in [condition]:
        query &= contains(condition)

    rich.print(search_files(files_to_search, query))
