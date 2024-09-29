import os
import re
import typer
import pyperclip
from rich import print


def parse_and_write_files(input_text, output_base_dir="."):
    file_pattern = re.compile(r"^#\s*(.+\.py)\s*$", re.MULTILINE)
    matches = list(file_pattern.finditer(input_text))

    if not matches:
        print("파일 경로 주석을 찾을 수 없습니다.")
        return

    for i, match in enumerate(matches):
        file_path = match.group(1).strip()
        start_index = match.end()

        if i + 1 < len(matches):
            end_index = matches[i + 1].start()
        else:
            end_index = len(input_text)

        file_content = input_text[start_index:end_index].strip()
        full_path = os.path.join(output_base_dir, file_path)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(file_content)

        print(f"파일 생성: {full_path}")


def paste_llm(
    output_dir: str = typer.Option(
        ".", help="파일을 생성할 기본 디렉토리 (기본값: 현재 디렉토리)"
    )
):
    """
    클립보드의 LLM 응답을 파싱하여 여러 Python 파일로 저장합니다.
    """
    try:
        content = pyperclip.paste()
    except pyperclip.PyperclipException as e:
        typer.echo(
            f"클립보드에서 텍스트를 가져오는 중 오류가 발생했습니다: {e}", err=True
        )
        raise typer.Exit(code=1)

    if not content.strip():
        typer.echo("클립보드에 텍스트가 비어 있습니다.", err=True)
        raise typer.Exit(code=1)

    parse_and_write_files(content, output_dir)
