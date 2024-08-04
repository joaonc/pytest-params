from pytest_params import params


@params('a', (('Foo', 1),))
def test_one_param_one_value(a):
    assert a == 1


@params('a', (('Foo', 1), ('Bar', 1)))
def test_one_param_multiple_values(a):
    assert a == 1


@params('a, b', (('Foo', 1, 2),))
def test_multiple_params_one_value(a, b):
    assert a == 1
    assert b == 2
