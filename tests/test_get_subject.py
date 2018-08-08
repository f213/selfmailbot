import pytest

from src.helpers import get_subject


@pytest.mark.parametrize('input, expected', [
    ['a b c d', 'A b c...'],
    ['a b   c d', 'A b c...'],
    ['a b', 'A b'],
    ['a b c', 'A b c'],
    ['1 2 3', '1 2 3'],  # ensure capfirst does not break on digits
    ['A b c', 'A b c'],
    [''.join('a' for _ in range(35)), 'A' + ''.join('a' for _ in range(31)) + '...'],
    [''.join('a' for _ in range(27)), 'A' + ''.join('a' for _ in range(26))],
])
def test_get_subject(input, expected):
    assert get_subject(input) == expected
