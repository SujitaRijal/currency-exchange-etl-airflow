import pytest
from include.utils.purge_utils import purge_old_files

def test_purge_old_files_directory_not_exists(tmp_path):
    missing_dir= tmp_path / "raw"

    purge_old_files(directory=missing_dir,retention_days=7, ds="2026-10-23")

def test_purge_old_files_deletes_old_files(tmp_path):
    #Arrange
    old_file= tmp_path / "2026-10-01.json"
    new_file=tmp_path / "2026-10-20.json"

    old_file.write_text("{}")
    new_file.write_text("{}")

    #Act
    purge_old_files(directory=tmp_path, retention_days=7, ds="2026-10-23")

    #Assert
    assert not old_file.exists()
    assert new_file.exists()

def test_purge_old_files_invalid_filename(tmp_path):
    invalid_file = tmp_path / "abc.json"
    invalid_file.write_text("{}")
    purge_old_files(directory=tmp_path, retention_days=7, ds= "2026-10-23")

    assert invalid_file.exists()
