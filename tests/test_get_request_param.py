from pytest_params import get_request_param


def test_get_request_param():
    assert get_request_param() == 'test2'
