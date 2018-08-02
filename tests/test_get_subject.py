import pytest

from src.helpers import get_subject


@pytest.mark.parametrize('input, expected', [
    ['a b c d', 'a b c...'],
    ['a b   c d', 'a b c...'],
    ['a b', 'a b'],
    ['a b c', 'a b c'],
    [''.join('a' for _ in range(35)), ''.join('a' for _ in range(32)) + '...'],
    [''.join('a' for _ in range(27)), ''.join('a' for _ in range(27))],
])
def test_get_subject(input, expected):
    assert get_subject(input) == expected
