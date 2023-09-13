"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import clone_client.proto.data_types_pb2
import google.protobuf.descriptor
import google.protobuf.message
import sys

if sys.version_info >= (3, 8):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing_extensions.final
class ValveListResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    VALVE_LIST_FIELD_NUMBER: builtins.int
    RESPONSE_FIELD_NUMBER: builtins.int
    @property
    def valve_list(self) -> clone_client.proto.data_types_pb2.MusclesValveInfo: ...
    @property
    def response(self) -> clone_client.proto.data_types_pb2.ServerResponse: ...
    def __init__(
        self,
        *,
        valve_list: clone_client.proto.data_types_pb2.MusclesValveInfo | None = ...,
        response: clone_client.proto.data_types_pb2.ServerResponse | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["response", b"response", "valve_list", b"valve_list"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["response", b"response", "valve_list", b"valve_list"]) -> None: ...

global___ValveListResponse = ValveListResponse

@typing_extensions.final
class CompressorInfoResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    INFO_FIELD_NUMBER: builtins.int
    RESPONSE_FIELD_NUMBER: builtins.int
    @property
    def info(self) -> global___CompressorInfo: ...
    @property
    def response(self) -> clone_client.proto.data_types_pb2.ServerResponse: ...
    def __init__(
        self,
        *,
        info: global___CompressorInfo | None = ...,
        response: clone_client.proto.data_types_pb2.ServerResponse | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["info", b"info", "response", b"response"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["info", b"info", "response", b"response"]) -> None: ...

global___CompressorInfoResponse = CompressorInfoResponse

@typing_extensions.final
class CompressorInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    IS_RUNNING_FIELD_NUMBER: builtins.int
    PRESSURE_FIELD_NUMBER: builtins.int
    DESIRED_PRESSURE_FIELD_NUMBER: builtins.int
    is_running: builtins.bool
    pressure: builtins.float
    desired_pressure: builtins.float
    def __init__(
        self,
        *,
        is_running: builtins.bool = ...,
        pressure: builtins.float = ...,
        desired_pressure: builtins.float = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["desired_pressure", b"desired_pressure", "is_running", b"is_running", "pressure", b"pressure"]) -> None: ...

global___CompressorInfo = CompressorInfo