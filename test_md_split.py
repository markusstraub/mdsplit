from md_split import split_by_h1
from md_split import get_valid_filename


def test_example():
    assert 1 == 1


def test_split_by_h1_simple():
    with open("test_resources/test_simple.md") as fh:
        parts = list(split_by_h1(fh))
        assert len(parts) == 2

        assert parts[0].header == "Header 1"
        assert len(parts[0].text) == 7
        assert parts[1].header == "Header 2"
        assert len(parts[1].text) == 3


def test_split_by_h1_codeblock():
    with open("test_resources/test_codeblock.md") as fh:
        parts = list(split_by_h1(fh))
        assert len(parts) == 4

        assert parts[0].header == "Header 1"
        assert len(parts[0].text) == 11
        assert parts[1].header == "Header 2 (dense)"
        assert len(parts[1].text) == 5
        assert parts[2].header == "Header 3 (with codeblocks)"
        assert len(parts[2].text) == 16
        assert parts[3].header == "Header 4"
        assert len(parts[3].text) == 3


def test_get_valid_filename():
    assert get_valid_filename("test.txt") == "test.txt"
    assert get_valid_filename("test with spaces-and-dashes") == "test with spaces-and-dashes"
    assert get_valid_filename("test/\\~#*+.txt") == "test.txt"
    assert get_valid_filename("non_ascii_Äß鳥_ჩიტები") == "non_ascii_Äß鳥_ჩიტები"
