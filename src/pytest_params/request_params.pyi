from typing import Any, Optional, TypeVar

T = TypeVar('T')

def get_request_param(request: Any, param: str, default: Optional[T] = None) -> Optional[T]: ...
