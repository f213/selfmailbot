import pytest

from src import recognize


@pytest.fixture
def recognition_result(mocker):
    return mocker.patch('src.recognize.do_recognition')


def test_success_recognition(recognition_result):
    recognition_result.return_value = ['Сходить в', 'магазин']

    assert recognize.recognize(b'testshit') == 'Сходить в магазин'


def test_no_recognition(recognition_result):
    recognition_result.return_value = []

    assert recognize.recognize(b'testshit') == ''
