from os import getcwd
from pathlib import Path
from unittest.mock import patch

import pytest

from mkdocs_plantuml_local.caching import has_cache, get_cache_path, get_cache, put_cache


@pytest.fixture(scope="function")
def hashed_list():
    hashed_list = ['foo', 'bar', 'baz']
    with patch('mkdocs_plantuml_local.caching.hash_list') as hash_list:
        hash_list.return_value = hashed_list
        yield hashed_list


def test_get_cache_path(hashed_list):
    path = get_cache_path(*hashed_list)
    assert str(path) == '/.cache/plantuml_local/foo/bar/baz'


def test_has_cache_when_no_cache_present():
    assert not has_cache()


def test_has_cache_when_cache_present(hashed_list, fs):
    fs.create_file(
        Path(getcwd()).joinpath(".cache", "plantuml_local", *hashed_list),
        contents="CACHE!",
    )
    assert has_cache(*hashed_list)


def test_get_cache_when_no_cache_present(hashed_list):
    assert get_cache(*hashed_list) is None


def test_get_cache_when_cache_present(hashed_list, fs):
    fs.create_file(
        Path(getcwd()).joinpath(".cache", "plantuml_local", *hashed_list),
        contents="CACHE!",
    )
    assert get_cache(*hashed_list) == b'CACHE!'


def test_put_cache_when_no_cache_present(hashed_list, fs):
    put_cache(b'NEW CACHE!', hashed_list)
    expected_path = Path(getcwd()).joinpath(".cache", "plantuml_local", *hashed_list)

    assert expected_path.read_bytes() == b'NEW CACHE!'


def test_put_cache_when_cache_present(hashed_list, fs):
    expected_path = Path(getcwd()).joinpath(".cache", "plantuml_local", *hashed_list)
    fs.create_file(expected_path, contents="CACHE!")

    put_cache(b'NEW CACHE!', hashed_list)

    assert expected_path.read_bytes() == b'NEW CACHE!'
