from collections import namedtuple
from pathlib import Path
import argparse
import re

DESCRIPTION = """Splits markdown files at level 1 headings.
For each chapter a new file with the (sanitized) heading name is written to the output folder.
"""
FENCES = ["```", "~~~"]

Chapter = namedtuple("Chapter", "header, text")


def split_by_h1(text):
    heading = None
    lines = []
    within_fence = False
    for line in text:
        if has_fence(line):
            within_fence = not within_fence

        new_chapter = is_heading(line) and not within_fence
        if new_chapter:
            if len(lines) > 0:
                yield Chapter(heading, lines)
            heading = line[2:].strip()
            lines = []

        lines.append(line)
    yield Chapter(heading, lines)


def is_heading(line):
    return line.startswith("# ")


def has_fence(line):
    for fence in FENCES:
        if line.startswith(fence):
            return True
    return False


def get_valid_filename(name):
    """
    Adapted from https://github.com/django/django/blob/main/django/utils/text.py
    """
    s = str(name).strip()
    s = re.sub(r"(?u)[^-\w. ]", "", s)
    if s in {"", ".", ".."}:
        raise ValueError(f"Could not derive file name from '{name}'")
    return s


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("input", help="input file")
    parser.add_argument("--output", help="output folder", default=None)
    args = parser.parse_args()
    print(args)

    out_path_str = args.output
    if out_path_str is None:
        out_path_str = Path(args.input).stem
    out_path = Path(get_valid_filename(out_path_str))
    out_path.mkdir(exist_ok=False)
    print(f"created output folder {out_path}")

    with open(args.input) as file:
        chapters = split_by_h1(file)
        for chapter in chapters:
            chapter_filename = get_valid_filename(chapter.header) + ".md"
            with open(out_path / chapter_filename, mode="w") as file:
                for line in chapter.text:
                    file.write(line)
            print(f"{chapter.header}: {len(chapter.text)} lines, file: '{chapter_filename}'")
