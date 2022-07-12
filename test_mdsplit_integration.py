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


def assert_same_file_contents(tmp_dir, expected_dir):
    for dir_path, dirs, files in os.walk(expected_dir):
        for file_name in files:
            expected_file = Path(dir_path, file_name)
            expected = expected_file.read_text()

            actual_file = tmp_dir / expected_file.relative_to(expected_dir)
            actual = actual_file.read_text()
            assert actual == expected, f"errror while comparing {expected_file}"


def test_fail_on_existing_output_directory(tmp_path, script_runner):
    ret = script_runner.run("mdsplit.py", "--output", str(tmp_path), "test_resources")
    assert not ret.success


def test_default_invocation(tmp_path, script_runner):
    ret = script_runner.run("mdsplit.py", "--output", str(tmp_path), "test_resources", "--force")
    assert ret.success
    assert_same_file_list(tmp_path, "test_expected/by_h1")
    assert_same_file_contents(tmp_path, "test_expected/by_h1")

    # is there a way to access the Stats object?
    # that would be more elegant than comparing stdout
    assert "- 7 input files" in ret.stdout
    assert "- 15 extracted chapters" in ret.stdout
    assert "- 13 new output files" in ret.stdout


def test_h3_split(tmp_path, script_runner):
    ret = script_runner.run(
        "mdsplit.py",
        "--output",
        str(tmp_path),
        "--max-level",
        "3",
        "test_resources/nested.md",
        "--force",
    )
    assert ret.success
    assert_same_file_list(tmp_path, "test_expected/by_h3/nested")
    assert_same_file_contents(tmp_path, "test_expected/by_h3/nested")
