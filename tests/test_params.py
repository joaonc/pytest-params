from src.pytest_params import params


def test_params():
    assert params() == 'test1'