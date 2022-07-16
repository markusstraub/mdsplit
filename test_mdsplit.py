import pytest
from mdsplit import Line
from mdsplit import get_valid_filename
from mdsplit import split_by_heading


def test_get_valid_filename():
    assert get_valid_filename("test.txt") == "test.txt"
    assert get_valid_filename("test with spaces-and-dashes") == "test with spaces-and-dashes"
    assert get_valid_filename("test/\\~#*+.txt") == "test.txt"
    assert get_valid_filename("non_ascii_Äß鳥_ჩიტები") == "non_ascii_Äß鳥_ჩიტები"


def test_line():
    line = Line("~~~")
    assert line.is_fence()

    line = Line("```bash")
    assert line.is_fence()

    line = Line("Not a header")
    assert not line.is_heading()

    line = Line("# Heading One")
    assert line.full_line == "# Heading One"
    assert line.is_heading()
    assert line.heading_level == 1
    assert line.heading_title == "Heading One"

    line = Line("###### Heading Six")
    assert line.full_line == "###### Heading Six"
    assert line.is_heading()
    assert line.heading_level == 6
    assert line.heading_title == "Heading Six"

    line = Line("####### Headings > 7 are not defined in Markdown")
    assert not line.is_heading()

    line = Line("   # Heading - up to three spaces are allowed according to commonmark")
    assert line.is_heading()

    line = Line("    # four spaces are too much")
    assert not line.is_heading()

    line = Line("#At least one space or tab required after heading")
    assert not line.is_heading()

    line = Line("#\ta tab is ok")
    assert line.is_heading()

    line = Line("###")  # headings without title (also without a space) are allowed
    assert line.heading_level == 3
    assert line.heading_title == ""

    line = Line("#\t  please strip\t\t  ")
    assert line.heading_title == "please strip"

    line = Line("## strip rightmost hashes #########  ")
    assert line.heading_title == "strip rightmost hashes"


@pytest.mark.parametrize("max_level", [1, 3])
def test_split_by_heading_simple(max_level):
    with open("test_resources/simple.md") as fh:
        chapters = list(split_by_heading(fh, max_level))

    assert len(chapters) == 2

    assert chapters[0].heading.heading_title == "Heading 1"
    assert chapters[0].heading.heading_level == 1
    assert chapters[0].parent_headings == []
    assert len(chapters[0].text) == 7
    assert chapters[1].heading.heading_title == "Heading 2"
    assert chapters[1].heading.heading_level == 1
    assert chapters[1].parent_headings == []
    assert len(chapters[1].text) == 3


@pytest.mark.parametrize("max_level", [1, 3])
def test_split_by_heading_codeblock(max_level):
    with open("test_resources/codeblock.md") as fh:
        chapters = list(split_by_heading(fh, max_level))

    assert len(chapters) == 1

    assert chapters[0].heading.heading_title == "Beware of Code Blocks"
    assert len(chapters[0].text) == 21


def test_split_by_h1_nested():
    with open("test_resources/nested.md") as fh:
        chapters = list(split_by_heading(fh, 1))

    assert len(chapters) == 3

    assert chapters[0].heading.heading_title == "Heading 1"
    assert len(chapters[0].text) == 13
    assert chapters[1].heading.heading_title == "Heading 2 (dense)"
    assert len(chapters[1].text) == 8
    assert chapters[2].heading.heading_title == "Heading 3 (deeply nested)"
    assert len(chapters[2].text) == 30


def test_split_by_h3_nested():
    with open("test_resources/nested.md") as fh:
        chapters = list(split_by_heading(fh, 3))

    assert len(chapters) == 11

    assert chapters[1].heading.heading_title == "Heading 1.1"
    assert chapters[1].heading.heading_level == 2
    assert chapters[1].parent_headings == ["Heading 1"]
    assert len(chapters[1].text) == 6

    assert chapters[2].heading.heading_title == "Heading 1.2"
    assert chapters[2].heading.heading_level == 2
    assert chapters[2].parent_headings == ["Heading 1"]
    assert len(chapters[2].text) == 3

    assert chapters[9].heading.heading_title == "Heading 3.1.1"
    assert chapters[9].heading.heading_level == 3
    assert chapters[9].parent_headings == ["Heading 3 (deeply nested)", "Heading 3.1"]
    assert len(chapters[9].text) == 22
