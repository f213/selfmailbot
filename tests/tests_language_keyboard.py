import pytest

from src.speech import get_language_keyboard


@pytest.fixture
def languages(mocker):
    return mocker.patch('src.speech.get_languages')


@pytest.mark.parametrize('input, expected', [
    (
        [['1', '2']],
        [['2 (1)']],
    ),
    (
        [['1', '2'], ['3', '4']],
        [['2 (1)', '4 (3)']],
    ),
    (
        [['1', '2'], ['3', '4'], ['5', '6']],
        [
            ['2 (1)', '4 (3)'],
            ['6 (5)'],
        ],
    ),
])
def test(input, expected, languages):
    languages.return_value = input

    assert get_language_keyboard() == expected
