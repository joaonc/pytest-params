# pytest-params

[![image](https://img.shields.io/pypi/v/pytest-params.svg)](https://pypi.python.org/pypi/pytest-params)

Simplified pytest test case parameters.

----

There are two main features in this package: the `@params` decorator and the `get_request_param`
function.

Note that this package is not a pytest plugin.

### `@params`

The main driver for this is that when test cases need parameters and could use a one-liner
description, using `@pytest.mark.parametrize` can get cumbersome.

`@params` is sugar syntax for `@pytest.mark.parametrize` that makes usage easier.

### `get_request_param`

When creating pytest fixtures that are to be called indirectly (with `indirect=True`), this small
function facilitates extracting the parameters used in the request, especially when there are
multiple parameters.

## Installation

```
$ pip install pytest-params
```

## Examples
### `@params`
Test case with a marker (`pri1`), `id` on each test case and one of the parameters needs to be
skipped.

pytest native, no `id`.

This is the most simple and common usage.  
Note how in the results report the values are displayed but there's no context provided. Also (not
in this example), sometimes the parameters can't be displayed correctly and what shows up in the
report is confusing.
```python
@pytest.mark.parametrize('a, b', [(1, 2), (3, 2), (0, 0)])
def test_foo(a, b):
    ...
```
```
============================= test session starts =============================
collecting ... collected 3 items

test_pytest_params.py::test_foo[1-2] PASSED                              [ 33%]
test_pytest_params.py::test_foo[3-2] PASSED                              [ 66%]
test_pytest_params.py::test_foo[0-0] PASSED                              [100%]

============================== 3 passed in 0.02s ==============================
```

pytest native, with `id`.

Context provided in each set of parameters. Much nicer in the results report.  
However, not straightforward to see which `id` corresponds to which set of parameters.
```python
@pytest.mark.parametrize(
    'a, b',
    [(1, 2), (3, 2), (0, 0)],
    ids=['Normal usage (a>b)', 'Inverted (a<b)', 'Both 0'],
)
def test_foo(a, b):
    ...
```
```
============================= test session starts =============================
collecting ... collected 3 items

test_pytest_params.py::test_foo[Normal usage (a>b)] PASSED               [ 33%]
test_pytest_params.py::test_foo[Inverted (a<b)] PASSED                   [ 66%]
test_pytest_params.py::test_foo[Both 0] PASSED                           [100%]

============================== 3 passed in 0.03s ==============================
```

Using `params`
```python
@params(
    'a, b',
    [
        ('Normal usage (a>b)', 1, 2),
        ('Inverted (a<b)', 3, 2, pytest.mark.pri1, pytest.mark.nightly),
        ('Both 0', 0, 0, pytest.mark.skip('BUG-123')),
    ]
)
def test_foo(a, b):
    ...
```
```
============================= test session starts =============================
collecting ... collected 3 items

test_pytest_params.py::test_foo[Normal usage (a>b)] PASSED               [ 33%]
test_pytest_params.py::test_foo[Inverted (a<b)] PASSED                   [ 66%]
test_pytest_params.py::test_foo[Both 0] SKIPPED (BUG-123)                [100%]
Skipped: BUG-123

================== 2 passed, 1 skipped, 2 warnings in 0.03s ===================
```

### `get_request_param`

## Features

**TODO**

### Similar projects

* [parametrization](https://github.com/singular-labs/parametrization)
* [pytest-parametrized](https://github.com/coady/pytest-parametrized)

The similarly named project [pytest-param](https://github.com/cr3/pytest-param) (no 's') is around
pytest parametrization, but not about making parameters easier to declare.
