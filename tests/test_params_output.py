from tests import TESTS_ROOT

TEST_MODULE = 'test_params.py'


def test_one_param_one_value(pytester):
    test_function = 'test_one_param_one_value'
    pytester.copy_example(TESTS_ROOT / TEST_MODULE)
    result = pytester.runpytest_inprocess('-v', '-rPfsxX', '-k', test_function)
    result.assert_outcomes(passed=1, failed=0)
    result.stdout.fnmatch_lines(
        [
            f"*{TEST_MODULE}::{test_function}[[]Foo[]]*",
        ]
    )


def test_one_param_multiple_values(pytester):
    test_function = 'test_one_param_multiple_values'
    pytester.copy_example(TESTS_ROOT / TEST_MODULE)
    result = pytester.runpytest_inprocess('-v', '-rPfsxX', '-k', test_function)
    result.assert_outcomes(passed=2, failed=0)
    result.stdout.fnmatch_lines(
        [
            f"*{TEST_MODULE}::{test_function}[[]Foo[]]*",
            f"*{TEST_MODULE}::{test_function}[[]Bar[]]*",
        ]
    )


def test_multiple_params_one_value(pytester):
    test_function = 'test_multiple_params_one_value'
    pytester.copy_example(TESTS_ROOT / TEST_MODULE)
    result = pytester.runpytest_inprocess('-v', '-rPfsxX', '-k', test_function)
    result.assert_outcomes(passed=1, failed=0)
    result.stdout.fnmatch_lines(
        [
            f"*{TEST_MODULE}::{test_function}[[]Foo[]]*",
        ]
    )
