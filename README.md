# pytest-params

[![image](https://img.shields.io/pypi/v/pytest-params.svg)](https://pypi.python.org/pypi/pytest-params)

Simplified pytest test case parameters.

----

## Installation

```
$ pip install pytest-params
```

## Examples
pytest native:
```python
@pytest.mark.parametrize('a', [1, 2, 3])
def test_foo(a):
    ...

```

## Features

**TODO**

### Similar projects

* [parametrization](https://github.com/singular-labs/parametrization)
* [pytest-parametrized](https://github.com/coady/pytest-parametrized)

The similarly named project [pytest-param](https://github.com/cr3/pytest-param) (no 's') is around
pytest parametrization, but not about making parameters easier to declare.
