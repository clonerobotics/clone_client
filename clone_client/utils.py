import asyncio
from contextlib import asynccontextmanager
from functools import wraps
import logging
import sys
from time import perf_counter
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    Type,
    TypeVar,
)
from urllib.parse import urlparse

from grpc import RpcError
from typing_extensions import Concatenate, ParamSpec

from clone_client.error_frames import translate_rpc_error

LOGGER = logging.getLogger(__name__)

PGrpc = ParamSpec("PGrpc")
RGrpc = TypeVar("RGrpc")
TGrpc = TypeVar("TGrpc")  # pylint: disable=invalid-name


def grpc_translated() -> (
    Callable[[Callable[Concatenate[TGrpc, PGrpc], RGrpc]], Callable[Concatenate[TGrpc, PGrpc], RGrpc]]
):
    """Decorator function to call async function with translated error from grpc."""

    def decorator(
        func: Callable[Concatenate[Any, PGrpc], RGrpc]
    ) -> Callable[Concatenate[TGrpc, PGrpc], RGrpc]:
        @wraps(func)
        async def wrapper(*args: PGrpc.args, **kwargs: PGrpc.kwargs) -> RGrpc:
            try:
                return await func(*args, **kwargs)
            except RpcError as err:
                golem_err = translate_rpc_error(func.__name__, args[0].socket_address, err)  # type: ignore
                raise golem_err from err

        return wrapper

    return decorator


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


def ensure_local(value: str) -> str:
    """Check if value ends with .local. and add it if not."""
    if value.endswith(".local."):
        return value

    return f"{value}.local."


PRetry = ParamSpec("PRetry")
RRetry = TypeVar("RRetry")
CatchType = Optional[List[Type[BaseException]]]


def retry(
    max_retries: int, catch: CatchType = None
) -> Callable[[Callable[PRetry, Awaitable[RRetry]]], Callable[PRetry, Awaitable[RRetry]]]:
    """Decorator for retrying an async function call."""

    def decorator(
        func: Callable[PRetry, Awaitable[RRetry]]
    ) -> Callable[PRetry, Callable[PRetry, Awaitable[RRetry]]]:
        async def wrapped(*args: PRetry.args, **kwargs: PRetry.kwargs) -> RRetry:
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

            return await func(*args, **kwargs)

        return wrapped

    return decorator


def strip_local(value: str) -> str:
    """Check if value ends with .local. and remove it if it does."""
    if value.endswith(".local."):
        return value.replace(".local.", "")

    return value


@asynccontextmanager
async def async_busy_ticker(
    dur: float, precision: float = 5, min_tick: float = 0.0005
) -> AsyncGenerator[None, None]:
    """
    Perform a tick every dur seconds and busy sleep until next tick for precise timing.

    WARNING: This might be resource intensive, use with caution.
    By tweaking precision and min_tick you can adjust the resource usage to precision ratio.
    Less precision means less resources used but less accurate timing.
    """
    next_tick = perf_counter() + dur

    yield

    elapsed = perf_counter() - next_tick
    # Sleep a fraction to save some resources
    await asyncio.sleep(max(0, (dur - elapsed) / precision))

    # Busy sleep until next tick for precise timing
    while perf_counter() < next_tick:
        await asyncio.sleep(min_tick)
