import logging
from typing import cast, Dict, Type

from grpc import Call, RpcError, StatusCode

from clone_client.exceptions import ClientError

from clone_client.proto.data_types_pb2 import ErrorInfo, ErrorType, ServerResponse


class ServerRequestError(ClientError):
    """Generic error returned by server to the client"""


class DataAcquisitionError(ServerRequestError):
    """Failed to collect requested data form state"""


class UnknownRpcError(ServerRequestError):
    """Unknown error has occurred"""


class ServerInstructionError(ServerRequestError):
    """Sent instructions were not handled properly"""


class ServerInvalidStateError(ServerRequestError):
    """Server current state doesn't allow to handle this type of request"""


class UnsupportedRequestError(ServerRequestError):
    """Server couldn't process sent request"""


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
ERROR_CODE_TRANSLATION: Dict[int, Type[ServerRequestError]] = {
    ErrorType.ACQUISITION: DataAcquisitionError,
    ErrorType.UNSUPPORTED_REQUEST: UnsupportedRequestError,
    ErrorType.INSTRUCTION: ServerInstructionError,
    ErrorType.INVALID_SERVER_STATE: ServerInvalidStateError,
    ErrorType.SERVICE_TIMEOUT: ServiceTimeoutError,
    ErrorType.RPC_TIMEOUT: RpcTimeoutError,
    ErrorType.UNKNOWN: UnknownRpcError,
}
# pylint: enable=no-member


LOGGER = logging.getLogger(__name__)


def get_request_error(error_info: ErrorInfo) -> ServerRequestError:
    """Translate error info to exception"""
    return ERROR_CODE_TRANSLATION[error_info.error](str(error_info.info))


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
