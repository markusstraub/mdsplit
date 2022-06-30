from collections import namedtuple
from pathlib import Path
import argparse
import os
import re

DESCRIPTION = """Splits markdown files at level 1 headings.
For each chapter a new file with the (sanitized) heading name is written to the output folder.
Text before the first heading is written to a file with the same name as the input file.
Chapters with the same heading are written to the same file.
"""
FENCES = ["```", "~~~"]
VERBOSE = False

Chapter = namedtuple("Chapter", "heading, text")


def split_by_h1(text):
    """
    Generator that returns a list of chapters.
    Each chapter's text includes the heading.
    """
    heading = None
    lines = []
    within_fence = False
    for line in text:
        if is_fence(line):
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


def is_fence(line):
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


def process_file(in_file_path, out_path):
    if VERBOSE:
        print(f"Process file '{in_file_path}' to '{out_path}'")
        print(f"Create output folder '{out_path}'")
    out_path.mkdir(parents=True, exist_ok=False)
    with open(in_file_path) as file:
        chapters = split_by_h1(file)
        for chapter in chapters:
            chapter_filename = get_valid_filename(chapter.heading) + ".md"
            if chapter.heading is None:
                chapter_filename = in_file_path.name
            chapter_path = out_path / chapter_filename
            if VERBOSE:
                print(f"Write {len(chapter.text)} lines to '{chapter_path}'")
            with open(chapter_path, mode="a") as file:
                for line in chapter.text:
                    file.write(line)


def process_directory(in_dir_path, out_path):
    for dir_path, dirs, files in os.walk(in_dir_path):
        for file_name in files:
            if not Path(file_name).suffix == ".md":
                continue
            file_path = Path(dir_path) / file_name
            new_out_path = out_path / os.path.relpath(dir_path, in_dir_path) / Path(file_name).stem
            process_file(file_path, new_out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("input", help="input file or folder")
    parser.add_argument("-o", "--output", help="output folder", default=None)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    VERBOSE = args.verbose

    in_path = Path(args.input)
    out_path_str = args.output

    if in_path.is_file():
        if out_path_str is None:
            out_path_str = in_path.stem
        process_file(in_path, Path(out_path_str))
    else:
        if out_path_str is None:
            out_path_str = in_path.stem + "_split"
        process_directory(in_path, Path(out_path_str))
