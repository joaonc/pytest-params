from typing import Any, Iterable, Literal, Sequence, Union

from _pytest.mark.structures import MarkDecorator, ParameterSet

# Define _ScopeName type for both pytest 7 and 8 compatibility
_ScopeName = Union[
    Literal['session'], Literal['package'], Literal['module'], Literal['class'], Literal['function']
]

def params(
    argnames: Union[str, Sequence[str]],
    name_values: Iterable[tuple],  # Iterable[tuple[str, ...]]
    *,
    indirect: Union[bool, Sequence[str]] = False,
    scope: Union[_ScopeName, None] = None,
) -> MarkDecorator: ...
def params_values(*name_values: Any) -> list[ParameterSet]: ...
