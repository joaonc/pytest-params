from typing import Iterable, Sequence

import pytest
from _pytest.mark.structures import MarkDecorator, ParameterSet
from _pytest.scope import _ScopeName

# `name_values` should have type `Iterable[tuple[str, ...]]`, which states the tuple has a string
# as first item and then an unknown number of items with any type. However, this declaration is not
# processed by `mypy`, so simplified it.


def params(
    argnames: str | Sequence[str],
    name_values: Iterable[tuple],  # Iterable[tuple[str, ...]]
    *,
    indirect: bool | Sequence[str] = False,
    scope: _ScopeName | None = None,
) -> MarkDecorator:
    argvalues = params_values(*name_values)
    return pytest.mark.parametrize(argnames, argvalues, indirect=indirect, scope=scope)


def params_values(*name_values) -> list[ParameterSet]:
    if not name_values:
        raise ValueError('Parameter needs to be iterable (usually list of lists).')
    if any(not hasattr(x, '__iter__') or isinstance(x, str) for x in name_values):
        raise ValueError('All items need to be iterable.')

    pytest_params = []
    errors = []
    for i, name_values_entry in enumerate(name_values):
        name_values_types = [
            type(x) for x in name_values_entry
        ]  # Avoid `isinstance` multiple times later.

        # Check if parameters `pytest.param(...)` are passed.
        name_values_params_indexes = [
            j for j, t in enumerate(name_values_types) if t == ParameterSet
        ]
        if name_values_params_indexes:
            # If a parameter is passed, then it needs to be the only one.
            if len(name_values_params_indexes) > 1:
                errors.append(
                    f'Entry {i}: When specifying `pytest.param(...)`, only one can be included. '
                    f'{len(name_values_params_indexes)} were added.'
                )
                continue
            if not all(
                t == MarkDecorator
                for j, t in enumerate(name_values_types)
                if j != name_values_params_indexes[0]
            ):
                errors.append(
                    f'Entry {i}: When specifying a `pytest.param(...)`, all other values need to '
                    'be `pytest.mark`. Other types were included.'
                )
                continue
            pytest_param = name_values_entry[name_values_params_indexes[0]]
            # Note: `MarkDecorator` is not hashable, so can't use sets to create a list of unique
            # marks. Potential for duplicate marks. If necessary can use `mark.name` to remove dups.
            marks = [
                x for j, x in enumerate(name_values_entry) if j != name_values_params_indexes[0]
            ]
            marks += pytest_param.marks
            pytest_params.append(
                pytest.param(*pytest_param.values, id=pytest_param.id, marks=marks)
            )
            continue

        # No `pytest.param(...)` is included.
        if len(name_values_entry) < 2:
            errors.append(
                f'Entry {i} needs to have at least 2 items, the first being the name of '
                f'the test case variant.'
            )
            continue
        testcase_id = name_values_entry[0]
        if not isinstance(testcase_id, str):
            errors.append(
                f'Entry {i} needs to have a string as the first item, which represents '
                f'the name of the test case variant.'
            )
            continue
        marks = [
            x
            for j, x in enumerate(name_values_entry[1:])
            if name_values_types[j + 1] == MarkDecorator
        ]
        values = [
            x
            for j, x in enumerate(name_values_entry[1:])
            if name_values_types[j + 1] != MarkDecorator
        ]
        if len(values) == 0:
            errors.append(f"Entry {i} doesn't contain any values.")
            continue
        pytest_params.append(pytest.param(*values, id=testcase_id, marks=marks))

    if not pytest_params:
        errors.append('No pytest parameters were extracted from the name/values list.')

    if errors:
        raise ValueError(
            f'{len(errors)} extracting parameters from the name/values list:\n' + '\n'.join(errors)
        )

    return pytest_params
