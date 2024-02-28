import pytest

from mkdocs_plantuml_local.hashing import hash_string, hash_list


@pytest.mark.parametrize('string,output', [
    ('test', 'n4bQgYhMfWWaL-qgxVrQFaO_TxsrC4Is0V1sFbDwCgg'),
])
def test_hashing_a_string(string, output):
    assert hash_string(string) == output


@pytest.mark.parametrize('string,output', [
    (
        ['unit', 'test'],
        [
            'OFz9vADsMgMWmUYHecFQmbK7o8rQ5ED_-wjhDfCsueE',
            'n4bQgYhMfWWaL-qgxVrQFaO_TxsrC4Is0V1sFbDwCgg',
        ],
    ),
])
def test_hashing_a_list(string, output):
    assert hash_list(string) == output
