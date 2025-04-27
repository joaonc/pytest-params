import pytest

from pytest_params import get_request_param

DEFAULT_VALUE = 'foobar'


@pytest.fixture
def my_fixture(request):
    """Fixture where the ``count`` parameter in the request is used."""
    return get_request_param(request, 'count', DEFAULT_VALUE)


def test_not_parametrized(my_fixture):
    """
    The fixture is used but not specified in ``@pytest.mark.parametrize``.
    Expected that the default value specified in the fixture is returned.
    """
    assert my_fixture == DEFAULT_VALUE


@pytest.mark.parametrize('my_fixture', [5])
def test_not_indirect(my_fixture):
    """
    The fixture is specified, but ``indirect=True`` is not specified.
    Expected that the value specified in ``@pytest.mark.parametrize`` is returned.
    """
    assert my_fixture == 5


@pytest.mark.parametrize('my_fixture', [{'count': 10}], indirect=True)
def test_parameter_specified(my_fixture):
    """
    Fixture used as intended, where the parameter is specified and ``indirect=True``.
    """
    assert my_fixture == 10


@pytest.mark.parametrize('my_fixture', [{}], indirect=True)
def test_no_key(my_fixture):
    """
    Fixture used with ``indirect=True``, and the parameter is a dictionary, but the required key
    is not specified.
    """
    assert my_fixture == DEFAULT_VALUE


@pytest.mark.parametrize('my_fixture', [20, None, 'a string'], indirect=True)
def test_parameter_not_key(my_fixture):
    """
    Fixture used with ``indirect=True`` but the parameter is not a dictionary.
    """
    assert my_fixture == DEFAULT_VALUE
