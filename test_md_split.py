import pytest
from md_split import MdSplit
from md_split import Line
from md_split import get_valid_filename


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


@pytest.mark.parametrize("max_level", [1, 3])
def test_split_by_heading_simple(max_level):
    with open("test_resources/simple.md") as fh:
        chapters = list(MdSplit.split_by_heading(fh, max_level))
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
        parts = list(MdSplit.split_by_heading(fh, max_level))
        assert len(parts) == 1

        assert parts[0].heading.heading_title == "Beware of Code Blocks"
        assert len(parts[0].text) == 21


def test_split_by_h1_nested():
    with open("test_resources/nested.md") as fh:
        parts = list(MdSplit.split_by_heading(fh, 1))
        assert len(parts) == 3

        assert parts[0].heading.heading_title == "Heading 1"
        assert len(parts[0].text) == 11
        assert parts[1].heading.heading_title == "Heading 2 (dense)"
        assert len(parts[1].text) == 8
        assert parts[2].heading.heading_title == "Heading 3 (deeply nested)"
        assert len(parts[2].text) == 30


def test_split_by_h3_nested():
    with open("test_resources/nested.md") as fh:
        parts = list(MdSplit.split_by_heading(fh, 3))
        assert len(parts) == 10
    # TODO test parent headings
