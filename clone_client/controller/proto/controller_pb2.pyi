"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""

import builtins
import clone_client.proto.data_types_pb2
import collections.abc
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class _PulseType:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _PulseTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_PulseType.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    IN: _PulseType.ValueType  # 0
    OUT: _PulseType.ValueType  # 1

class PulseType(_PulseType, metaclass=_PulseTypeEnumTypeWrapper):
    """Controlling muscles by sending a pulse to open / close the valve using timed oscilations."""

IN: PulseType.ValueType  # 0
OUT: PulseType.ValueType  # 1
global___PulseType = PulseType

@typing.final
class SetPressuresMessage(google.protobuf.message.Message):
    """Controling muslces by directly setting an absolute value of a pressure"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    PRESSURES_FIELD_NUMBER: builtins.int
    @property
    def pressures(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.float]: ...
    def __init__(
        self,
        *,
        pressures: collections.abc.Iterable[builtins.float] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["pressures", b"pressures"]) -> None: ...

global___SetPressuresMessage = SetPressuresMessage

@typing.final
class Impulse(google.protobuf.message.Message):
    """Controlling musles by setting a timed impulse to open / close the valve"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    VALUE_FIELD_NUMBER: builtins.int
    IGNORE_FIELD_NUMBER: builtins.int
    value: builtins.float
    ignore: builtins.bool
    def __init__(
        self,
        *,
        value: builtins.float = ...,
        ignore: builtins.bool = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["data", b"data", "ignore", b"ignore", "value", b"value"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["data", b"data", "ignore", b"ignore", "value", b"value"]) -> None: ...
    def WhichOneof(self, oneof_group: typing.Literal["data", b"data"]) -> typing.Literal["value", "ignore"] | None: ...

global___Impulse = Impulse

@typing.final
class SetImpulsesMessage(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    IMPULSES_FIELD_NUMBER: builtins.int
    @property
    def impulses(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___Impulse]: ...
    def __init__(
        self,
        *,
        impulses: collections.abc.Iterable[global___Impulse] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["impulses", b"impulses"]) -> None: ...

global___SetImpulsesMessage = SetImpulsesMessage

@typing.final
class PulseValue(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    CTRL_TYPE_FIELD_NUMBER: builtins.int
    PULSE_LEN_MS_FIELD_NUMBER: builtins.int
    DELAY_LEN_MS_FIELD_NUMBER: builtins.int
    DURATION_MS_FIELD_NUMBER: builtins.int
    ctrl_type: global___PulseType.ValueType
    pulse_len_ms: builtins.float
    delay_len_ms: builtins.float
    duration_ms: builtins.float
    def __init__(
        self,
        *,
        ctrl_type: global___PulseType.ValueType = ...,
        pulse_len_ms: builtins.float = ...,
        delay_len_ms: builtins.float = ...,
        duration_ms: builtins.float = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["ctrl_type", b"ctrl_type", "delay_len_ms", b"delay_len_ms", "duration_ms", b"duration_ms", "pulse_len_ms", b"pulse_len_ms"]) -> None: ...

global___PulseValue = PulseValue

@typing.final
class Pulse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    VALUE_FIELD_NUMBER: builtins.int
    IGNORE_FIELD_NUMBER: builtins.int
    ignore: builtins.bool
    @property
    def value(self) -> global___PulseValue: ...
    def __init__(
        self,
        *,
        value: global___PulseValue | None = ...,
        ignore: builtins.bool = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["data", b"data", "ignore", b"ignore", "value", b"value"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["data", b"data", "ignore", b"ignore", "value", b"value"]) -> None: ...
    def WhichOneof(self, oneof_group: typing.Literal["data", b"data"]) -> typing.Literal["value", "ignore"] | None: ...

global___Pulse = Pulse

@typing.final
class SetPulsesMessage(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    PULSES_FIELD_NUMBER: builtins.int
    @property
    def pulses(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___Pulse]: ...
    def __init__(
        self,
        *,
        pulses: collections.abc.Iterable[global___Pulse] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["pulses", b"pulses"]) -> None: ...

global___SetPulsesMessage = SetPulsesMessage

@typing.final
class ControllerRuntimeConfig(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    MAX_IMPULSE_DURATION_MS_FIELD_NUMBER: builtins.int
    USE_PUMP_FIELD_NUMBER: builtins.int
    ALLOW_MISSING_NODES_FIELD_NUMBER: builtins.int
    max_impulse_duration_ms: builtins.int
    use_pump: builtins.bool
    allow_missing_nodes: builtins.bool
    def __init__(
        self,
        *,
        max_impulse_duration_ms: builtins.int = ...,
        use_pump: builtins.bool = ...,
        allow_missing_nodes: builtins.bool = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["allow_missing_nodes", b"allow_missing_nodes", "max_impulse_duration_ms", b"max_impulse_duration_ms", "use_pump", b"use_pump"]) -> None: ...

global___ControllerRuntimeConfig = ControllerRuntimeConfig

@typing.final
class WaterPumpPressure(google.protobuf.message.Message):
    """Water pump control"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    PRESSURE_FIELD_NUMBER: builtins.int
    pressure: builtins.float
    def __init__(
        self,
        *,
        pressure: builtins.float = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["pressure", b"pressure"]) -> None: ...

global___WaterPumpPressure = WaterPumpPressure

@typing.final
class WaterPumpInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    DESIRED_PRESSURE_FIELD_NUMBER: builtins.int
    PRESSURE_FIELD_NUMBER: builtins.int
    IS_RUNNING_FIELD_NUMBER: builtins.int
    IS_ACTIVE_FIELD_NUMBER: builtins.int
    TEMPERATURE_FIELD_NUMBER: builtins.int
    desired_pressure: builtins.float
    pressure: builtins.float
    is_running: builtins.bool
    is_active: builtins.bool
    temperature: builtins.float
    def __init__(
        self,
        *,
        desired_pressure: builtins.float = ...,
        pressure: builtins.float = ...,
        is_running: builtins.bool = ...,
        is_active: builtins.bool = ...,
        temperature: builtins.float = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["desired_pressure", b"desired_pressure", "is_active", b"is_active", "is_running", b"is_running", "pressure", b"pressure", "temperature", b"temperature"]) -> None: ...

global___WaterPumpInfo = WaterPumpInfo

@typing.final
class WaterPumpInfoResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    INFO_FIELD_NUMBER: builtins.int
    RESPONSE_FIELD_NUMBER: builtins.int
    @property
    def info(self) -> global___WaterPumpInfo: ...
    @property
    def response(self) -> clone_client.proto.data_types_pb2.ServerResponse: ...
    def __init__(
        self,
        *,
        info: global___WaterPumpInfo | None = ...,
        response: clone_client.proto.data_types_pb2.ServerResponse | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["info", b"info", "response", b"response"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["info", b"info", "response", b"response"]) -> None: ...

global___WaterPumpInfoResponse = WaterPumpInfoResponse
