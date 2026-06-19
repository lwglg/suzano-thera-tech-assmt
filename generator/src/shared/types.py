from typing import NotRequired, TypedDict

__all__ = [
    "GenericError",
    "GenericResult",
]


class GenericError(TypedDict):
    name: str
    description: str
    stack_trace: NotRequired[list[str]]


class GenericResult[T](TypedDict):
    result: NotRequired[T]
    errors: NotRequired[GenericError | list[GenericError]]
