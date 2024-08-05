from typing import Any


def get_request_param(request, param: str, default: Any = None) -> Any:
    if hasattr(request, 'param') and isinstance(request.param, dict):
        return request.param.get(param, default)
    return default
