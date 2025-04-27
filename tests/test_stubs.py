from pytest_params import get_request_param, params, params_values


# Test that the stubs are working
def test_function():
    @params(
        'param',
        [
            ('test1', 1),
            ('test2', 2),
        ],
    )
    def test_example(param):
        assert param in (1, 2)

    # Test params_values
    values = params_values(('test1', 1), ('test2', 2))
    assert len(values) == 2

    # Test get_request_param
    class MockRequest:
        param = {'key': 'value'}

    request = MockRequest()
    value = get_request_param(request, 'key', 'default')
    assert value == 'value'

    missing = get_request_param(request, 'missing', 'default')
    assert missing == 'default'
