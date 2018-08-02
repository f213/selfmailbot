from src import mail

URL = 'https://api.mailgun.net/v3/samples.mailgun.org/messages'


def test_get_url():
    assert mail.get_url() == URL


def test_auth(requests_mock):
    def assertions(request, *args):
        assert request.headers['Authorization'] == 'Basic YXBpOmtleS0zYXg2eG5qcDI5amQ2ZmRzNGdjMzczc2d2anh0ZW9sMA=='  # encoded default password from pytest.ini

        return {}

    requests_mock.post(URL, json=assertions)

    mail.post({'random': 'stuff'})


def test_params(requests_mock):
    def assertions(request, *args):
        assert 'stuff' in request.body
        assert 'random' in request.body

        return {}

    requests_mock.post(URL, json=assertions)

    mail.post({'random': 'stuff'})
