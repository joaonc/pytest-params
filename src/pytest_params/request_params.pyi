from typing import Any, TypeVar, Optional

T = TypeVar('T')

def get_request_param(request: Any, param: str, default: T = None) -> Optional[T]: ...
