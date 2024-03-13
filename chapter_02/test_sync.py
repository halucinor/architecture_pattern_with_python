import tempfile
from pathlib import Path
from sync import sync
import shutil


def test_when_a_file_exists_in_the_source_but_not_in_the_destination():
    try:
        source = tempfile.mkdtemp()
        dest = tempfile.mkdtemp()

        content = "I am a very useful file"
        (Path(source) / "file1").write_text(content)

        sync(source, dest)

        expected_path = Path(dest) / "file1"
        assert expected_path.exists()
        assert expected_path.read_text() == content

    finally:
        shutil.rmtree(source)
        shutil.rmtree(dest)


def test_when_a_file_has_been_renamed_in_the_source():
    try:
        source = tempfile.mkdtemp()
        dest = tempfile.mkdtemp()

        content = "I am a file that was renamed"
        source_path = Path(source) / "source_file"
        old_dest_path = Path(dest) / "dest_file"

        expected_path = Path(dest) / "source_file"
        source_path.write_text(content)
        old_dest_path.write_text(content)

        sync(source, dest)

        assert old_dest_path.exists() is False
        assert expected_path.read_text() == content

    finally:
        shutil.rmtree(source)
        shutil.rmtree(dest)
