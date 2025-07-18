# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: clone_client/proto/controller.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'clone_client/proto/controller.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from clone_client.proto import data_types_pb2 as clone__client_dot_proto_dot_data__types__pb2
from clone_client.proto import hardware_driver_pb2 as clone__client_dot_proto_dot_hardware__driver__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n#clone_client/proto/controller.proto\x12\x10\x63lone.controller\x1a\x1bgoogle/protobuf/empty.proto\x1a#clone_client/proto/data_types.proto\x1a(clone_client/proto/hardware_driver.proto\"(\n\x13SetPressuresMessage\x12\x11\n\tpressures\x18\x01 \x03(\x02\"4\n\x07Impulse\x12\x0f\n\x05value\x18\x01 \x01(\x02H\x00\x12\x10\n\x06ignore\x18\x02 \x01(\x08H\x00\x42\x06\n\x04\x64\x61ta\"A\n\x12SetImpulsesMessage\x12+\n\x08impulses\x18\x01 \x03(\x0b\x32\x19.clone.controller.Impulse\"}\n\nPulseValue\x12.\n\tctrl_type\x18\x01 \x01(\x0e\x32\x1b.clone.controller.PulseType\x12\x14\n\x0cpulse_len_ms\x18\x02 \x01(\x02\x12\x14\n\x0c\x64\x65lay_len_ms\x18\x03 \x01(\x02\x12\x13\n\x0b\x64uration_ms\x18\x04 \x01(\x02\"P\n\x05Pulse\x12-\n\x05value\x18\x01 \x01(\x0b\x32\x1c.clone.controller.PulseValueH\x00\x12\x10\n\x06ignore\x18\x02 \x01(\x08H\x00\x42\x06\n\x04\x64\x61ta\";\n\x10SetPulsesMessage\x12\'\n\x06pulses\x18\x02 \x03(\x0b\x32\x17.clone.controller.Pulse\"i\n\x17\x43ontrollerRuntimeConfig\x12\x1f\n\x17max_impulse_duration_ms\x18\x01 \x01(\r\x12\x10\n\x08use_pump\x18\x02 \x01(\x08\x12\x1b\n\x13\x61llow_missing_nodes\x18\x03 \x01(\x08\"%\n\x11WaterPumpPressure\x12\x10\n\x08pressure\x18\x01 \x01(\x02\"w\n\rWaterPumpInfo\x12\x18\n\x10\x64\x65sired_pressure\x18\x01 \x01(\x02\x12\x10\n\x08pressure\x18\x02 \x01(\x02\x12\x12\n\nis_running\x18\x03 \x01(\x08\x12\x11\n\tis_active\x18\x04 \x01(\x08\x12\x13\n\x0btemperature\x18\x05 \x01(\x02\"z\n\x15WaterPumpInfoResponse\x12-\n\x04info\x18\x01 \x01(\x0b\x32\x1f.clone.controller.WaterPumpInfo\x12\x32\n\x08response\x18\x02 \x01(\x0b\x32 .clone.data_types.ServerResponse*\x1c\n\tPulseType\x12\x06\n\x02IN\x10\x00\x12\x07\n\x03OUT\x10\x01\x32\xea\x0c\n\x0e\x43ontrollerGRPC\x12U\n\x0bSetImpulses\x12$.clone.controller.SetImpulsesMessage\x1a .clone.data_types.ServerResponse\x12Q\n\tSetPulses\x12\".clone.controller.SetPulsesMessage\x1a .clone.data_types.ServerResponse\x12W\n\x0cSetPressures\x12%.clone.controller.SetPressuresMessage\x1a .clone.data_types.ServerResponse\x12H\n\x0cLooseMuscles\x12\x16.google.protobuf.Empty\x1a .clone.data_types.ServerResponse\x12G\n\x0bLockMuscles\x12\x16.google.protobuf.Empty\x1a .clone.data_types.ServerResponse\x12_\n\x12StreamSetPressures\x12%.clone.controller.SetPressuresMessage\x1a .clone.data_types.ServerResponse(\x01\x12n\n\x15SendPinchValveControl\x12\x33.clone.hardware_driver.SendPinchValveControlMessage\x1a .clone.data_types.ServerResponse\x12v\n\x19SendManyPinchValveControl\x12\x37.clone.hardware_driver.SendManyPinchValveControlMessage\x1a .clone.data_types.ServerResponse\x12z\n\x1bStreamManyPinchValveControl\x12\x37.clone.hardware_driver.SendManyPinchValveControlMessage\x1a .clone.data_types.ServerResponse(\x01\x12n\n\x15SendPinchValveCommand\x12\x33.clone.hardware_driver.SendPinchValveCommandMessage\x1a .clone.data_types.ServerResponse\x12v\n\x19SendManyPinchValveCommand\x12\x37.clone.hardware_driver.SendManyPinchValveCommandMessage\x1a .clone.data_types.ServerResponse\x12S\n\x10GetWaterPumpInfo\x12\x16.google.protobuf.Empty\x1a\'.clone.controller.WaterPumpInfoResponse\x12J\n\x0eStartWaterPump\x12\x16.google.protobuf.Empty\x1a .clone.data_types.ServerResponse\x12I\n\rStopWaterPump\x12\x16.google.protobuf.Empty\x1a .clone.data_types.ServerResponse\x12]\n\x14SetWaterPumpPressure\x12#.clone.controller.WaterPumpPressure\x1a .clone.data_types.ServerResponse\x12N\n\tGetConfig\x12\x16.google.protobuf.Empty\x1a).clone.controller.ControllerRuntimeConfig\x12\x42\n\x08GetNodes\x12\x16.google.protobuf.Empty\x1a\x1e.clone.hardware_driver.NodeMap\x12\x36\n\x04Ping\x12\x16.google.protobuf.Empty\x1a\x16.google.protobuf.Emptyb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'clone_client.proto.controller_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_PULSETYPE']._serialized_start=989
  _globals['_PULSETYPE']._serialized_end=1017
  _globals['_SETPRESSURESMESSAGE']._serialized_start=165
  _globals['_SETPRESSURESMESSAGE']._serialized_end=205
  _globals['_IMPULSE']._serialized_start=207
  _globals['_IMPULSE']._serialized_end=259
  _globals['_SETIMPULSESMESSAGE']._serialized_start=261
  _globals['_SETIMPULSESMESSAGE']._serialized_end=326
  _globals['_PULSEVALUE']._serialized_start=328
  _globals['_PULSEVALUE']._serialized_end=453
  _globals['_PULSE']._serialized_start=455
  _globals['_PULSE']._serialized_end=535
  _globals['_SETPULSESMESSAGE']._serialized_start=537
  _globals['_SETPULSESMESSAGE']._serialized_end=596
  _globals['_CONTROLLERRUNTIMECONFIG']._serialized_start=598
  _globals['_CONTROLLERRUNTIMECONFIG']._serialized_end=703
  _globals['_WATERPUMPPRESSURE']._serialized_start=705
  _globals['_WATERPUMPPRESSURE']._serialized_end=742
  _globals['_WATERPUMPINFO']._serialized_start=744
  _globals['_WATERPUMPINFO']._serialized_end=863
  _globals['_WATERPUMPINFORESPONSE']._serialized_start=865
  _globals['_WATERPUMPINFORESPONSE']._serialized_end=987
  _globals['_CONTROLLERGRPC']._serialized_start=1020
  _globals['_CONTROLLERGRPC']._serialized_end=2662
# @@protoc_insertion_point(module_scope)
