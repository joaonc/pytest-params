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
Some examples are provided here. For more examples with advanced usage, please see the test cases
under `tests`.

### `@params`

#### pytest native, no `id`.
This is the most common and simple usage.  
Note how in the results report the values are displayed but there's no context provided.  
Also (not in this example), sometimes the parameters can't be displayed correctly and what shows
in the report is confusing.
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

#### pytest native, with `id`.
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

#### Using `params`
Compared to the examples above that use pytest's `@pytest.mark.parametrize`:
* Easier to see which description matches which parameters, given they're all together.
* Ability to have markers in individual sets of parameters.

  Using pytest's native functionality, this is done by creating instances of `pytest.param` and
  use that as parameters, which is more convoluted and verbose, making it less readable and overall
  less used.

  Note that by having these markers, the test cases behave as when `@pytest.mark` is applied to the
  test function without parameters. For example if you wanted to run only `pri1` tests, using the
  `-m pri1` parameters would execute only the parameter set `'Inverted (a<b)'`.
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
Running only the `pri1` tests with `-m pr1` parameter.  
Note how only the `'Inverted (a<b)'` variant ran, which contains the `pri1` marker.
```
============================= test session starts =============================
collecting ... collected 3 items / 2 deselected / 1 selected

test_pytest_params.py::test_foo[Inverted (a<b)] PASSED                   [100%]

================= 1 passed, 2 deselected, 2 warnings in 0.02s =================
```

### `get_request_param`

This function helps in cases where a fixture requires multiple arguments.

The example below shows the `rectangle` fixture using `get_request_param()` and the test cases
using that fixture passing the `w` and `h` arguments in the form of a dictionary.

Also shows different ways to implement test cases, including not using `get_request_param()`.

Note that this example is rather simple and may not illustrate the usefulness of the
`get_request_param`, but as the test cases grow in number and complexity, this comes in handy. 

```python
from dataclasses import dataclass
import pytest
from src.pytest_params import params, get_request_param

@dataclass
class Rectangle:
    width: float
    height: float

    def area(self) -> float:
        return self.width * self.height


@pytest.fixture
def rectangle(request):
    width = get_request_param(request, 'w')
    height = get_request_param(request, 'h')

    return Rectangle(width=width, height=height)


@pytest.mark.parametrize(
    'w, h, expected',
    [
        (3, 2, 6),
        (2, 4, 8),
    ],
)
def test_area_1(w, h, expected):
    """
    Not using the `rectangle` fixture.
    Need to instantiate `Rectangle` in the test case.
    """
    rectangle = Rectangle(width=w, height=h)
    assert rectangle.area() == expected


@pytest.mark.parametrize(
    'rectangle',
    [
        {'w': 3, 'h': 2},
        {'w': 2, 'h': 3},
    ],
    indirect=True,
)
def test_area_2(rectangle):
    """
    Using the `rectangle` fixture with `@pytest.mark.parametrize` and `indirect=True`.
    Having `indirect=True` means that all arguments are fixtures that will be called indirectly.
    """
    assert rectangle.area() == 6


@params(
    'rectangle, expected',
    [
        ('W > H', {'w': 3, 'h': 2}, 6),
        ('W < H', {'w': 2, 'h': 4}, 8),
        ('W = H', {'w': 4, 'h': 4}, 16),
        ('W is 0', {'w': 0, 'h': 4}, 0),
        ('Both 0', {'w': 0, 'h': 0}, 0),
    ],
    indirect=['rectangle'],
)
def test_area_3(rectangle, expected):
    """
    Using the `rectangle` fixture with `@params` and `indirect=['rectangle']`.
    Having `indirect=['rectangle']` means that other parameters can be used without being called
    indirectly, in this case we can have the `expected` parameter. Note that this is not particular
    to `@params` and can be done with `@pytest.mark.parametrize` as well.
    """
    assert rectangle.area() == expected
```
```
============================= test session starts =============================
collecting ... collected 9 items

test_pytest_params.py::test_area_1[3-2-6] PASSED                         [ 11%]
test_pytest_params.py::test_area_1[2-4-8] PASSED                         [ 22%]
test_pytest_params.py::test_area_2[rectangle0] PASSED                    [ 33%]
test_pytest_params.py::test_area_2[rectangle1] PASSED                    [ 44%]
test_pytest_params.py::test_area_3[W > H] PASSED                         [ 55%]
test_pytest_params.py::test_area_3[W < H] PASSED                         [ 66%]
test_pytest_params.py::test_area_3[W = H] PASSED                         [ 77%]
test_pytest_params.py::test_area_3[W is 0] PASSED                        [ 88%]
test_pytest_params.py::test_area_3[Both 0] PASSED                        [100%]

============================== 9 passed in 0.05s ==============================
```

### Similar projects

* [parametrization](https://github.com/singular-labs/parametrization)
* [pytest-parametrized](https://github.com/coady/pytest-parametrized)

The similarly named project [pytest-param](https://github.com/cr3/pytest-param) (no 's') is around
pytest parametrization, but not about making parameters easier to declare.
