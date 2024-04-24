import asyncio
import logging
import sys
from typing import Awaitable, Callable, Dict, List, Optional, Protocol, Type, TypeVar
from urllib.parse import urlparse

from google.protobuf.message import Message
from typing_extensions import ParamSpec

LOGGER = logging.getLogger(__name__)


def url_rfc_to_grpc_py39(address: str) -> str:
    """
    Parses RFC1808 compliant URL (with leading slashes)
    to format accepted by grpc.
    Works only with python 3.9. Use url_rfc_to_grpc for higher versions.
    """
    parsed_url = urlparse(address)
    if parsed_url.scheme in ["", "ipv4", "ipv6", "dns"]:
        return f"{parsed_url.scheme}:{parsed_url.netloc}"

    # Conversion not needed
    return address


def url_rfc_to_grpc(address: str) -> str:
    """Parses RFC1808 compliant URL (with leading slashes)
    to format accepted by grpc"""

    # Currently we want to support 3.9 for a while but changes in urllib.parse
    # breaks the implementation so usage with 3.11 is not possible without changes
    # and project compatible with only 3.9 won't work with project marked as compatible with ^3.9
    # hence this double implementation.
    # Remove this function when we drop support for 3.9
    if "3.9" in sys.version:
        return url_rfc_to_grpc_py39(address)

    parsed_url = urlparse(address)
    if parsed_url.scheme in ["http", "https", "ipv4", "ipv6", "dns"]:
        return parsed_url.netloc

    if parsed_url.scheme == "":
        return parsed_url.path

    # Conversion not needed
    return address


# pylint: disable=too-few-public-methods
class IsDataclass(Protocol):
    """Protocol for dataclasses."""

    __dataclass_fields__: Dict


T = TypeVar("T", bound=IsDataclass)


def convert_grpc_instance_to_own_representation(data_to_convert: Message, target_class: Type[T]) -> T:
    """Converts a grpc instance to a dataclass instance."""
    info = {}

    for attr in target_class.__dataclass_fields__.keys():
        info[attr] = getattr(data_to_convert, attr)

    return target_class(**info)


def ensure_local(value: str) -> str:
    """Check if value ends with .local. and add it if not."""
    if value.endswith(".local."):
        return value

    return f"{value}.local."


P = ParamSpec("P")
R = TypeVar("R")
CatchType = Optional[List[Type[BaseException]]]


def retry(
    max_retries: int, catch: CatchType = None
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Decorator for retrying an async function call."""

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Callable[P, Awaitable[R]]]:
        async def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:  # type: ignore
            for curr_retry in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as err:  # pylint: disable=broad-except
                    if catch is None or any(isinstance(err, error) for error in catch):
                        if curr_retry == max_retries:
                            raise

                        LOGGER.warning(
                            "Retrying %s, attempt %d/%d", func.__name__, curr_retry + 1, max_retries
                        )
                        await asyncio.sleep(curr_retry / 2)
                    else:
                        raise

        return wrapped  # type: ignore

    return decorator  # type: ignore


def strip_local(value: str) -> str:
    """Check if value ends with .local. and remove it if it does."""
    if value.endswith(".local."):
        return value.replace(".local.", "")

    return value
