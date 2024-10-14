import os
import re
import random
import typer
from typing import Optional, List
from rich import print
from rich.syntax import Syntax
import pyperclip

def find_files_with_keyword(
    directory: str,
    keyword: Optional[str] = None,
    exclude_keywords: Optional[List[str]] = None,
) -> list:
    matching_files = []
    for root, dirs, files in os.walk(directory):
        if exclude_keywords:
            dirs[:] = [d for d in dirs if not any(kw in d for kw in exclude_keywords)]
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                if exclude_keywords and any(kw in full_path for kw in exclude_keywords):
                    continue
                if keyword and not contains_keyword(full_path, keyword):
                    continue

                module_path = convert_path_to_module(full_path, directory)
                matching_files.append((module_path, full_path))

    return matching_files

def contains_keyword(file_path: str, keyword: str) -> bool:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            result = keyword in content
            return result
    except Exception as e:
        error_message = f"Error reading file {file_path}: {e}"
        typer.echo(error_message, err=True)
        return False


def convert_path_to_module(file_path: str, base_directory: str) -> str:
    rel_path = os.path.relpath(file_path, base_directory)
    module_path = rel_path.replace(os.path.sep, ".")[:-3]  # .py 제거

    # 상위 디렉토리 이름을 포함한 전체 모듈 경로 생성
    parent_dir = os.path.basename(os.path.dirname(base_directory))
    full_module_path = f"{parent_dir}.{module_path}"

    return full_module_path

def get_file_line_count(file_path: str) -> int:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return sum(1 for line in file if line.strip())  # 빈 줄 제외
    except Exception as e:
        typer.echo(f"Error reading file {file_path}: {e}", err=True)
        return 0

def select_random_files(matching_files: list, max_lines: int = 15000):
    selected_files = []
    total_lines = 0
    available_files = matching_files.copy()

    while available_files and total_lines < max_lines:
        selected = random.choice(available_files)
        file_lines = get_file_line_count(selected[1])

        if total_lines + file_lines <= max_lines:
            selected_files.append(selected)
            total_lines += file_lines

        available_files.remove(selected)

    return selected_files, total_lines

def generate_import_string(selected_files: list) -> str:
    import_lines = [f"import {file}" for file in selected_files]
    code_line = "%code " + " ".join(selected_files)
    return "\n".join(import_lines + ["", code_line])

"""
"""

def copy_import(
    directory: str = typer.Argument(..., help="Directory to search for Python files"),
    keyword: Optional[str] = typer.Option(
        None, help="Keyword to search for in file names and contents"
    ),
    exclude_keywords: Optional[List[str]] = typer.Option(
        None, help="Keywords to exclude from file paths (e.g. migrations)"
    ),
    max_lines: Optional[int] = typer.Option(
        15000, help="Maximum total lines of selected files"
    ),
):
    """
    Generate import strings from selected Python files and copy them to clipboard.
    """
    matching_files = find_files_with_keyword(directory, keyword, exclude_keywords)
    if max_lines:
        selected_files, total_lines = select_random_files(matching_files, max_lines)
    else:
        selected_files = matching_files
        total_lines = sum(get_file_line_count(path) for _, path in matching_files)

    if not selected_files:
        typer.echo("선택된 파일이 없습니다.", err=True)
        raise typer.Exit()

    result_string = generate_import_string(selected_files)

    print(f"[bold]검색 디렉토리:[/bold] {directory}")
    print(f"[bold]검색 키워드:[/bold] {keyword}")
    print(
        f"[bold]제외 키워드:[/bold] {', '.join(exclude_keywords) if exclude_keywords else 'None'}"
    )
    print(f"[bold]선택된 파일 수:[/bold] {len(selected_files)}")
    print(f"[bold]총 줄 수:[/bold] {total_lines}")
    print("\n[bold]생성된 import 문자열:[/bold]")
    print(result_string)

    pyperclip.copy(result_string)
    print("\n[green]생성된 import 문자열이 클립보드에 복사되었습니다.[/green]")

def copy_context(
    directory: str = typer.Argument(..., help="Directory to search for Python files"),
    keyword: Optional[str] = typer.Option(
        None, help="Keyword to search for in file names and contents"
    ),
    exclude: Optional[str] = typer.Option(
        None, help="Keywords to exclude from file paths (e.g. migrations)"
    ),
    max_lines: Optional[int] = typer.Option(
        15000, help="Maximum total lines of selected files"
    ),
):
    """
    Select Python files and copy their entire content as context to clipboard.
    """
    if "," in exclude:
        exclude = exclude.split(",")

    matching_files = find_files_with_keyword(directory, keyword, exclude)
    if max_lines:
        selected_files, total_lines = select_random_files(matching_files, max_lines)
    else:
        selected_files = [file for file, path in matching_files]
        total_lines = sum(get_file_line_count(path) for _, path in matching_files)

    if not selected_files:
        typer.echo("선택된 파일이 없습니다.", err=True)
        raise typer.Exit()

    context_strings = []
    for module, path in selected_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            header = f"# {path}"
            context_strings.append(header)
            context_strings.append(content)
        except Exception as e:
            typer.echo(f"파일을 읽는 중 오류 발생 {path}: {e}", err=True)

    combined_context = "\n\n".join(context_strings)

    print(f"[bold]direcory:[/bold] {directory}")
    print(f"[bold]keyword  :[/bold] {keyword}")
    print(
        f"[bold]exclude  :[/bold] {', '.join(exclude) if exclude else 'None'}"
    )
    print(f"[bold]선택된 파일 수:[/bold] {len(selected_files)}")
    for file, path in matching_files:
        print(f"  - {file} ({get_file_line_count(path)} lines)")

    print(f"[bold]총 줄 수:[/bold] {total_lines}")
    print("\n[bold]생성된 컨텍스트 문자열:[/bold]", len(combined_context))

    pyperclip.copy(combined_context)
    print("\n[green]생성된 컨텍스트 문자열이 클립보드에 복사되었습니다.[/green]")
