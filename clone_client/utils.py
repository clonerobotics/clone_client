import asyncio
from contextlib import asynccontextmanager, contextmanager
from functools import wraps
import logging
import sys
from time import get_clock_info, perf_counter, perf_counter_ns, sleep
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    Protocol,
    Type,
    TypeVar,
)
from urllib.parse import urlparse
import warnings

from grpc import RpcError
from typing_extensions import Concatenate, ParamSpec

from clone_client.error_frames import translate_rpc_error

LOGGER = logging.getLogger(__name__)

PGrpc = ParamSpec("PGrpc")
RGrpc = TypeVar("RGrpc")
TGrpc = TypeVar("TGrpc")  # pylint: disable=invalid-name


def grpc_translated_async() -> (
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


def grpc_translated() -> (
    Callable[[Callable[Concatenate[TGrpc, PGrpc], RGrpc]], Callable[Concatenate[TGrpc, PGrpc], RGrpc]]
):
    """Decorator function to call function with translated error from grpc."""

    def decorator(
        func: Callable[Concatenate[Any, PGrpc], RGrpc]
    ) -> Callable[Concatenate[TGrpc, PGrpc], RGrpc]:
        @wraps(func)
        def wrapper(*args: PGrpc.args, **kwargs: PGrpc.kwargs) -> RGrpc:
            try:
                return func(*args, **kwargs)
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


def strip_local(value: str) -> str:
    """Check if value ends with .local. and remove it if it does."""
    if value.endswith(".local."):
        return value.replace(".local.", "")

    return value


def _precise_interval_base(interval: float, precision: float = 0.2) -> Generator[int | None, None, None]:
    """
    Interval ticks for precise timings.

    Parameters:
    - interval: Duration between each tick in seconds.
    - precision: The precision of the tick, higher precision means more resources used.
                 Smaller intervals require more precision.
    """
    if precision < 0 or precision > 1:
        raise ValueError("Precision must be between 0 and 1")

    if interval < 0:
        interval = 0
        LOGGER.warning("Negative interval specified (%d). Setting to 0.", interval)

    interval_ns = int(interval * 1e9)
    resolution = get_clock_info("perf_counter").resolution
    min_tick_ns = int(resolution * 1e9)
    fraction = max(resolution, (1 - precision))

    try:
        while True:
            next_tick = perf_counter_ns() + interval_ns

            yield None

            remaining = next_tick - perf_counter_ns()
            if remaining < 0:
                remaining = 0
                LOGGER.warning(
                    "Tick takes longer than specified interval (%d). Please consider increasing it. ",
                    remaining,
                )

            if fraction > 0:
                yield int(remaining * fraction)

            while perf_counter_ns() < next_tick:
                yield min_tick_ns

    except GeneratorExit:
        pass


def _busy_ticker_base(
    dur: float, precision: float = 5, min_tick: float = 0.0005
) -> Generator[int | None, None, None]:
    """
    Perform a tick every dur seconds and busy sleep until next tick for precise timing.

    WARNING: This might be resource intensive, use with caution.
    By tweaking precision and min_tick you can adjust the resource usage to precision ratio.
    Less precision means less resources used but less accurate timing.
    """

    if precision < 0 or precision > 1:
        raise ValueError("Precision must be between 0 and 1")

    if dur < 0:
        dur = 0
        LOGGER.warning("Negative duration specified (%d). Setting to 0.", dur)

    dur_ns = int(dur * 1e9)
    min_tick_ns = int(min_tick * 1e9)
    next_tick = perf_counter_ns() + dur_ns

    try:
        while True:
            yield None

            elapsed = perf_counter_ns() - next_tick
            # Sleep a fraction to save some resources
            yield max(0, (dur_ns - elapsed) / precision)

            # Busy sleep until next tick for precise timing
            while perf_counter() < next_tick:
                yield min_tick_ns

    except GeneratorExit:
        pass


async def async_precise_interval(interval: float, precision: float = 0.2) -> AsyncGenerator[None, None]:
    for sleep_time_ns in _precise_interval_base(interval, precision):
        if sleep_time_ns is not None:
            await asyncio.sleep(sleep_time_ns / 1e9)
        else:
            yield


@asynccontextmanager
async def async_busy_ticker(
    dur: float, precision: float = 5, min_tick: float = 0.0005
) -> AsyncGenerator[None, None]:
    warnings.warn("This function is deprecated, use async_precise_interval instead", DeprecationWarning)
    for sleep_time_ns in _busy_ticker_base(dur, precision, min_tick):
        if sleep_time_ns is not None:
            await asyncio.sleep(sleep_time_ns / 1e9)
        else:
            yield


def precise_interval(interval: float, precision: float = 0.2) -> Generator[None, None, None]:
    for sleep_time_ns in _precise_interval_base(interval, precision):
        if sleep_time_ns is not None:
            sleep(sleep_time_ns / 1e9)
        else:
            yield


@contextmanager
def busy_ticker(dur: float, precision: float = 5, min_tick: float = 0.0005) -> Generator[None, None, None]:
    warnings.warn("This function is deprecated, use precise_interval instead", DeprecationWarning)
    for sleep_time_ns in _busy_ticker_base(dur, precision, min_tick):
        if sleep_time_ns is not None:
            sleep(sleep_time_ns / 1e9)
        else:
            yield
