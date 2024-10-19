import os
from pathlib import Path


def list_files(in_path):
    collected = set()
    for dir_path, dirs, files in os.walk(in_path):
        for file_name in files:
            collected.add(str(Path(dir_path, file_name).relative_to(in_path)))
    print(in_path, collected)
    return collected


def assert_same_file_list(actual_dir, expected_dir):
    assert list_files(actual_dir) == list_files(expected_dir)


def assert_same_file_contents(tmp_dir, expected_dir, encoding=None):
    for dir_path, dirs, files in os.walk(expected_dir):
        for file_name in files:
            expected_file = Path(dir_path, file_name)
            expected = expected_file.read_text(encoding=encoding)

            actual_file = tmp_dir / expected_file.relative_to(expected_dir)
            actual = actual_file.read_text(encoding=encoding)
            print("----")
            print(actual)
            print("----")
            assert actual == expected, f"errror while comparing {expected_file}"


def test_fail_on_existing_output_directory(tmp_path, script_runner):
    ret = script_runner.run(["mdsplit.py", "--output", str(tmp_path), "tests/test_resources"])
    assert not ret.success


def test_default_h1_split(tmp_path, script_runner):
    # --force required because the tmp_path will already be created
    ret = script_runner.run(
        [
            "mdsplit.py",
            "tests/test_resources",
            "--output",
            str(tmp_path),
            "--table-of-contents",
            "--force",
        ]
    )
    assert ret.success
    assert_same_file_list(tmp_path, "tests/test_expected/by_h1")
    assert_same_file_contents(tmp_path, "tests/test_expected/by_h1")

    # is there a way to access the Stats object?
    # that would be more elegant than comparing stdout
    assert "- 8 input file(s)" in ret.stdout
    assert "- 17 extracted chapter(s)" in ret.stdout
    assert "- 23 new output file(s)" in ret.stdout


def test_h3_split(tmp_path, script_runner):
    ret = script_runner.run(
        [
            "mdsplit.py",
            "tests/test_resources/nested.md",
            "--output",
            str(tmp_path),
            "--max-level",
            "3",
            "--table-of-contents",
            "--force",
        ]
    )
    assert ret.success
    assert_same_file_list(tmp_path, "tests/test_expected/by_h3/nested")
    assert_same_file_contents(tmp_path, "tests/test_expected/by_h3/nested")


def test_h3_split_with_navigation(tmp_path, script_runner):
    ret = script_runner.run(
        [
            "mdsplit.py",
            "tests/test_resources/nested.md",
            "--output",
            str(tmp_path),
            "--max-level",
            "3",
            "--table-of-contents",
            "--navigation",
            "--force",
        ]
    )
    assert ret.success
    assert_same_file_list(tmp_path, "tests/test_expected/by_h3/nested_with_navigation")
    assert_same_file_contents(tmp_path, "tests/test_expected/by_h3/nested_with_navigation")


def test_encoding(tmp_path, script_runner):
    ret = script_runner.run(
        [
            "mdsplit.py",
            "tests/test_resources_encoding/cp1252.md",
            "--encoding",
            "cp1252",
            "--output",
            str(tmp_path),
            "--force",
        ]
    )
    assert ret.success
    assert_same_file_list(tmp_path, "tests/test_expected/encoding")
    assert_same_file_contents(tmp_path, "tests/test_expected/encoding", encoding="cp1252")
    pass


# TODO how could we test stdin handling?
