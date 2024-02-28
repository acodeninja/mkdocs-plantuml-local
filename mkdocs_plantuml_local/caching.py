from pathlib import Path
from os import getcwd

from mkdocs_plantuml_local.hashing import hash_list


def get_cache_path(*data) -> Path:
    path = Path(getcwd())
    return path.joinpath('.cache', 'plantuml_local', *hash_list(data))


def has_cache(*data) -> bool:
    return get_cache_path(*data).exists()


def get_cache(*data) -> bytes:
    path = get_cache_path(*data)
    if path.exists():
        return path.read_bytes()


def put_cache(contents, *data):
    path = get_cache_path(*data)

    if not path.parent.exists():
        path.parent.mkdir(parents=True)

    path.write_bytes(contents)
