from src.services.file import set_file_name, set_file_path, split_path_and_name

from .conftest import (
    FILE_NAME,
    FILE_PATH,
    FILE_PATH_WITH_FILE_NAME,
    ROOT_PATH,
    UPLOAD_FILE_NAME,
)


def test_set_file_path_none():
    assert set_file_path(None) == ROOT_PATH
    assert set_file_path(ROOT_PATH) == ROOT_PATH

    assert set_file_path(FILE_PATH_WITH_FILE_NAME) == FILE_PATH
    assert set_file_path(FILE_PATH_WITH_FILE_NAME[1:]) == FILE_PATH

    assert set_file_path(FILE_PATH) == FILE_PATH
    assert set_file_path(FILE_PATH[1:]) == FILE_PATH
    assert set_file_path(FILE_PATH[:-1]) == ROOT_PATH


def test_set_file_name(upload_file):
    assert set_file_name(FILE_PATH_WITH_FILE_NAME, upload_file) == FILE_NAME
    assert set_file_name(None, upload_file) == UPLOAD_FILE_NAME
    assert set_file_name(FILE_NAME, upload_file) == FILE_NAME
    assert set_file_name(FILE_PATH, upload_file) == UPLOAD_FILE_NAME
    assert set_file_name(FILE_PATH, upload_file) == UPLOAD_FILE_NAME


def test_split_path_and_name():
    assert split_path_and_name(FILE_PATH_WITH_FILE_NAME) == (
        FILE_PATH,
        FILE_NAME,
    )
    assert split_path_and_name(FILE_PATH_WITH_FILE_NAME[1:]) == (
        FILE_PATH,
        FILE_NAME,
    )
    assert split_path_and_name(FILE_NAME) == (
        ROOT_PATH,
        FILE_NAME,
    )
    assert split_path_and_name(ROOT_PATH + FILE_NAME) == (
        ROOT_PATH,
        FILE_NAME,
    )
