import os
from pathlib import Path


def list_files(in_path):
    collected = set()
    for dir_path, dirs, files in os.walk(in_path):
        for file_name in files:
            collected.add(str(Path(dir_path, file_name).relative_to(in_path)))
    return collected


def assert_same_file_list(actual_dir, expected_dir):
    assert list_files(actual_dir) == list_files(expected_dir)


def assert_same_file_contents(tmp_dir, expected_dir):
    for dir_path, dirs, files in os.walk(expected_dir):
        for file_name in files:
            expected_file = Path(dir_path, file_name)
            expected = expected_file.read_text()

            actual_file = tmp_dir / expected_file.relative_to(expected_dir)
            actual = actual_file.read_text()
            assert actual == expected, f"errror while comparing {expected_file}"


def test_default_invocation(tmp_path, script_runner):
    ret = script_runner.run("md_split.py", "--output", str(tmp_path), "test_resources")
    assert ret.success
    assert_same_file_list(tmp_path, "test_expected/by_h1")
    assert_same_file_contents(tmp_path, "test_expected/by_h1")
