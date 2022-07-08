from collections import namedtuple
from pathlib import Path
import argparse
import os
import re
import sys

FENCES = ["```", "~~~"]
MAX_HEADING_LEVEL = 6

Chapter = namedtuple("Chapter", "parent_headings, heading, text")


class MdSplit:
    """Split markdown files into chapters at a given heading level.

    Each chapter (or subchapter) is written to its own file,
    which is named after the heading title.
    These files are written to subdirectories representing the document's structure.

    Note:
    - The output is *guaranteed to be identical* with the input
      (except for the separation into multiple files of course).
        - This means: no touching of whitespace or changing `-` to `*` of your lists
          like some viusual markdown editors tend to do.
    - Text before the first heading is written to a file with the same name as the markdown file.
    - Chapters with the same heading name are written to the same file.
    - Only ATX headings (such as # Heading 1) are supported.
    """

    def __init__(self, in_path, out_path=None, verbose=False, level=1):
        self.in_path = Path(in_path)
        if not self.in_path.exists():
            raise MdSplitError(f"Input file/directory '{self.in_path}' does not exist. Exiting..")
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
    """
    Detect code blocks and ATX headings.

    Headings are detected according to commonmark, e.g.:
    - only 6 valid levels
    - up to three spaces before the first # is ok
    - empty heading is valid
    - closing hashes are stripped
    - whitespace around title are stripped
    """

    def __init__(self, line):
        self.full_line = line
        self._detect_heading(line)

    def _detect_heading(self, line):
        self.heading_level = 0
        self.heading_title = None
        result = re.search("^[ ]{0,3}(#+)(.*)", line)
        if result is not None and (len(result[1]) <= MAX_HEADING_LEVEL):
            title = result[2]
            if len(title) > 0 and not (title.startswith(" ") or title.startswith("\t")):
                # if there is a title it must start with space or tab
                return
            self.heading_level = len(result[1])

            # strip whitespace and closing hashes
            title = title.strip().rstrip("#").rstrip()
            self.heading_title = title

    def is_fence(self):
        for fence in FENCES:
            if self.full_line.startswith(fence):
                return True
        return False

    def is_heading(self):
        return self.heading_level > 0


class MdSplitError(Exception):
    """MdSplit must stop but has an explanation string to be shown to the user"""


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
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description=MdSplit.__doc__
    )
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

    try:
        MdSplit(
            args.input, out_path=args.output, verbose=args.verbose, level=args.max_level
        ).process()
    except MdSplitError as e:
        print(e)
        sys.exit(1)
    # TODO we should not write to existing folder.. or should we?


if __name__ == "__main__":
    run()