from enum import auto, IntEnum
import logging
from typing import cast, Dict, Type

from grpc import Call, RpcError, StatusCode

from clone_client.exceptions import ClientError
from clone_client.proto.data_types_pb2 import ErrorInfo, ErrorType, ServerResponse

### ServerResponse ERRORS BELOW


class ServerRequestError(ClientError):
    """Generic error returned by server to the client"""


class InternalGolemServerRequestError(ClientError):
    """Error generated directly by a Golem server, with an ErrorType"""

    def __init__(self, error_info: ErrorInfo | str) -> None:
        if isinstance(error_info, ErrorInfo):
            error_info = f"ServerResponse error: {error_info.info}"
        super().__init__(error_info)


class UnknownGolemError(InternalGolemServerRequestError):
    """Server answered with an error which it could not classify"""


class GolemError(InternalGolemServerRequestError):
    """Request failed with GolemError"""

    class ErrorKind(IntEnum):
        """Types of golem errors"""

        GRPC = 1  # Caused by a GRPC error (tonic::Status) (in source)
        SNAIL_PROTO = auto()  # Caused by a SnailProtoError (in source)
        IO = auto()  # Caused by an IO error (in source)
        MISSING_HARDWARE = auto()  # When some hardware, e.g. node or a bus is missing
        DISABLED_FUNCTIONALITY = auto()  # When a functionality is disabled (e.g. telemetry)
        WRONG_REQUEST = auto()  # When a wrong request comes from remote
        CONFIGURATION = auto()  # When configuration is malformed or cannot be read during startup
        REMOTE_GOLEM_ERROR = auto()  # When one golem's unit receives an error from another one
        RUNTIME_ERROR = auto()  # Error from a runtime, e.g. Tokio

    def __init__(self, error_info: ErrorInfo) -> None:
        self.kind = GolemError.ErrorKind(error_info.subtype)
        message = f"ServerResponse GolemError({self.kind!r}): {error_info.info}"
        super().__init__(message)


class WrongRequestError(InternalGolemServerRequestError):
    """Server couldn't process sent request due to wrong parameters"""


class DisabledFunctionalityError(InternalGolemServerRequestError):
    """Server seems to have the selected functionality disabled"""


### RPC ERRORS BELOW


class UnknownRpcError(ServerRequestError):
    """Unknown error has occurred"""


class ServerInstructionError(ServerRequestError):
    """Sent instructions were not handled properly"""


class ServerInvalidStateError(ServerRequestError):
    """Server current state doesn't allow to handle this type of request"""


class ChannelUnavailableError(ServerRequestError):
    """Channel which the rpc tried to connect is not available"""

    def __init__(self, call_name: str, channel: str):
        message = f"Call to {call_name} failed, because client could not connect to chanel: {channel}."
        super().__init__(message)


class RpcTimeoutError(ServerRequestError):
    """Got timeout connecting to RPC"""

    def __init__(self, call_name: str, channel: str):
        message = f"Call to {call_name} on channel {channel} timed out."
        super().__init__(message)


class ServiceTimeoutError(ServerRequestError):
    """Got timeout connecting to RPC"""

    def __init__(self, call_name: str):
        message = f"Call to {call_name} timed out internally."
        super().__init__(message)


# pylint: disable=no-member
ERROR_TYPE_TRANSLATION: Dict[int, Type[InternalGolemServerRequestError]] = {
    ErrorType.UNKNOWN: UnknownGolemError,
    ErrorType.GOLEM_ERROR: GolemError,
    ErrorType.WRONG_REQUEST: WrongRequestError,
    ErrorType.DISABLED_FUNCTIONALITY: DisabledFunctionalityError,
}
# pylint: enable=no-member


LOGGER = logging.getLogger(__name__)


def get_request_error(error_info: ErrorInfo) -> InternalGolemServerRequestError:
    """Translate error info to exception"""
    return ERROR_TYPE_TRANSLATION[error_info.error](error_info)


def translate_rpc_error(rpc_name: str, channel: str, error: RpcError) -> ClientError:  # type: ignore
    """Translate gRPC error to ClientError"""
    error = cast(Call, error)  # type: ignore
    if error.code() == StatusCode.UNAVAILABLE:
        LOGGER.error(
            "Call to %s on channel: %s failed: could not connect to channel",
            rpc_name,
            channel,
        )
        return ChannelUnavailableError(rpc_name, channel)

    if error.code() == StatusCode.DEADLINE_EXCEEDED:
        LOGGER.error("Call to rpc %s on channel %s timed out!", rpc_name, channel)
        timeout_err = RpcTimeoutError(rpc_name, channel)
        return timeout_err

    if error.code() == StatusCode.UNKNOWN:
        LOGGER.error(
            "Call to %s resulted in unknown gRPC error. Details: %s",
            rpc_name,
            error.details(),
        )
        return UnknownRpcError(error.details())

    LOGGER.error("Call to %s resulted in unknown gRPC error", rpc_name)
    return UnknownRpcError(error.code(), error.details())


def handle_response(response: ServerResponse) -> None:
    """Handle response from server"""
    if response.success:
        if response.HasField("error"):
            LOGGER.exception(
                "Received non-critical exception from server: [Code: %s] %s",
                ErrorType.Name(response.error.error),  # pylint: disable=no-member
                response.error.info,
            )
        return
    if response.error:
        raise get_request_error(response.error)
    raise ClientError("Unknown error has occurred")
