from typing import Optional, TypeVar

T = TypeVar('T')


def get_request_param(request, param: str, default: Optional[T] = None) -> Optional[T]:
    if hasattr(request, 'param') and isinstance(request.param, dict):
        return request.param.get(param, default)
    return default
