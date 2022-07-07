from collections import namedtuple
from pathlib import Path
import argparse
import os
import re

FENCES = ["```", "~~~"]
MAX_HEADING_LEVEL = 6

Chapter = namedtuple("Chapter", "parent_headings, heading, text")


class MdSplit:
    """Split markdown files at headings.

    For each chapter a new file with the (sanitized) heading name is written to the output folder.
    If splitting is requested for heading levels > 1 a folder structure is created.
    Text before the first heading is written to a file with the same name as the input file.
    Chapters with the same heading are written to the same file.
    """

    def __init__(self, in_path, out_path=None, verbose=False, level=1):
        self.in_path = Path(in_path)
        if not self.in_path.exists():
            raise FileNotFoundError(
                f"Input file/directory '{self.in_path}' does not exist. Exiting.."
            )
        elif self.in_path.is_file():
            self.out_path = Path(self.in_path.stem) if out_path is None else Path(out_path)
        else:
            self.out_path = (
                Path(self.in_path.stem + "_split") if out_path is None else Path(out_path)
            )
        # if self.out_path.exists():
        #    raise FileExistsError(f"Output directory '{self.out_path}' already exists. Exiting..")
        self.verbose = verbose
        self.level = level

    def process(self):
        if self.in_path.is_file():
            self.process_file(self.in_path, self.out_path)
        else:
            self.process_directory(self.in_path, Path(self.out_path))

    def process_directory(self, in_dir_path, out_path):
        for dir_path, dirs, files in os.walk(in_dir_path):
            for file_name in files:
                if not Path(file_name).suffix == ".md":
                    continue
                file_path = Path(dir_path) / file_name
                new_out_path = (
                    out_path / os.path.relpath(dir_path, in_dir_path) / Path(file_name).stem
                )
                self.process_file(file_path, new_out_path)

    def process_file(self, in_file_path, out_path):
        if self.verbose:
            print(f"Process file '{in_file_path}' to '{out_path}'")
            print(f"Create output folder '{out_path}'")
        with open(in_file_path) as file:
            chapters = self.split_by_heading(file, self.level)
            for chapter in chapters:
                chapter_dir = out_path
                for parent in chapter.parent_headings:
                    chapter_dir = chapter_dir / get_valid_filename(parent)
                chapter_dir.mkdir(parents=True, exist_ok=True)

                chapter_filename = (
                    in_file_path.name
                    if chapter.heading is None
                    else get_valid_filename(chapter.heading.heading_title) + ".md"
                )

                chapter_path = chapter_dir / chapter_filename
                if self.verbose:
                    print(f"Write {len(chapter.text)} lines to '{chapter_path}'")
                with open(chapter_path, mode="a") as file:
                    for line in chapter.text:
                        file.write(line)

    @staticmethod
    def split_by_heading(text, max_level):
        """
        Generator that returns a list of chapters from text.
        Each chapter's text includes the heading line.
        """
        curr_parent_headings = []
        curr_heading_line = None
        curr_lines = []
        within_fence = False
        for next_line in text:
            next_line = Line(next_line)

            if next_line.is_fence():
                within_fence = not within_fence

            is_chapter_finished = (
                not within_fence and next_line.is_heading() and next_line.heading_level <= max_level
            )
            if is_chapter_finished:
                if len(curr_lines) > 0:
                    yield Chapter(list(curr_parent_headings), curr_heading_line, curr_lines)

                    if curr_heading_line is not None:
                        if curr_heading_line.heading_level > next_line.heading_level:
                            curr_parent_headings.pop()
                        if curr_heading_line.heading_level < next_line.heading_level:
                            curr_parent_headings.append(curr_heading_line.heading_title)

                curr_heading_line = next_line
                curr_lines = []

            curr_lines.append(next_line.full_line)
        yield Chapter(curr_parent_headings, curr_heading_line, curr_lines)


class Line:
    def __init__(self, line):
        self.full_line = line
        self.heading_level = 0
        self.heading_title = None

        result = re.search("(#+) (.*)", line)
        if result is not None and len(result[1]) <= MAX_HEADING_LEVEL:
            self.heading_level = len(result[1])
            self.heading_title = result[2]

    def is_fence(self):
        for fence in FENCES:
            if self.full_line.startswith(fence):
                return True
        return False

    def is_heading(self):
        return self.heading_level > 0


def get_valid_filename(name):
    """
    Adapted from https://github.com/django/django/blob/main/django/utils/text.py
    """
    s = str(name).strip()
    s = re.sub(r"(?u)[^-\w. ]", "", s)
    if s in {"", ".", ".."}:
        raise ValueError(f"Could not derive file name from '{name}'")
    return s


def run():
    parser = argparse.ArgumentParser(description=MdSplit.__doc__)
    parser.add_argument("input", help="input file or folder")
    parser.add_argument(
        "-l",
        "--max-level",
        type=int,
        choices=range(1, MAX_HEADING_LEVEL + 1),
        help="maximum heading level to split, default: %(default)s",
        default=1,
    )
    parser.add_argument("-o", "--output", help="output folder", default=None)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    MdSplit(args.input, out_path=args.output, verbose=args.verbose, level=args.max_level).process()
    # TODO no stacktrace for user errors (in file does not exist)
    # TODO we should not write to existing folder.. or should we?
    # TODO document that the lines stay exactly the same :)


if __name__ == "__main__":
    run()
