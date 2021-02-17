from src.ci_utils import parse


def test_parse_correct_keys():
    """Test that parse sets both ref and head_commit correctly."""
    data = {
        'ref': 'refs/heads/ci_server',
        'head_commit': {
            'id': '3f28d0dd76b9b1bdd5db5224a1012e5738d2b7b5',
        }
    }
    res = parse(data)
    assert res['branch'] == 'ci_server'
    assert res['head_commit'] == '3f28d0dd76b9b1bdd5db5224a1012e5738d2b7b5'


def test_parse_missing_keys():
    """Test that parse sets error if key does not exist."""
    data = {}
    res = parse(data)

    assert 'ref' not in res
    assert 'head_commit' not in res
    assert res['error'] == 'Missing key'
