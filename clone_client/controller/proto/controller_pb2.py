# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: clone_client/controller/proto/controller.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from clone_client.proto import data_types_pb2 as clone__client_dot_proto_dot_data__types__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n.clone_client/controller/proto/controller.proto\x12\x10\x63lone.controller\x1a\x1bgoogle/protobuf/empty.proto\x1a#clone_client/proto/data_types.proto\"i\n\x17\x43ontrollerRuntimeConfig\x12\x1f\n\x17max_impulse_duration_ms\x18\x01 \x01(\r\x12\x10\n\x08use_pump\x18\x02 \x01(\x08\x12\x1b\n\x13\x61llow_missing_nodes\x18\x03 \x01(\x08\"\x7f\n\x11ValveListResponse\x12\x36\n\nvalve_list\x18\x01 \x01(\x0b\x32\".clone.data_types.MusclesValveInfo\x12\x32\n\x08response\x18\x02 \x01(\x0b\x32 .clone.data_types.ServerResponse\"w\n\rWaterPumpInfo\x12\x18\n\x10\x64\x65sired_pressure\x18\x01 \x01(\x02\x12\x10\n\x08pressure\x18\x02 \x01(\x02\x12\x12\n\nis_running\x18\x03 \x01(\x08\x12\x11\n\tis_active\x18\x04 \x01(\x08\x12\x13\n\x0btemperature\x18\x05 \x01(\x02\"z\n\x15WaterPumpInfoResponse\x12-\n\x04info\x18\x01 \x01(\x0b\x32\x1f.clone.controller.WaterPumpInfo\x12\x32\n\x08response\x18\x02 \x01(\x0b\x32 .clone.data_types.ServerResponse2\xc0\x06\n\x0e\x43ontrollerGRPC\x12S\n\x10GetWaterPumpInfo\x12\x16.google.protobuf.Empty\x1a\'.clone.controller.WaterPumpInfoResponse\x12J\n\x0eStartWaterPump\x12\x16.google.protobuf.Empty\x1a .clone.data_types.ServerResponse\x12I\n\rStopWaterPump\x12\x16.google.protobuf.Empty\x1a .clone.data_types.ServerResponse\x12]\n\x14SetWaterPumpPressure\x12#.clone.data_types.WaterPumpPressure\x1a .clone.data_types.ServerResponse\x12P\n\nSetMuscles\x12 .clone.data_types.MuscleMovement\x1a .clone.data_types.ServerResponse\x12H\n\x0cLooseMuscles\x12\x16.google.protobuf.Empty\x1a .clone.data_types.ServerResponse\x12G\n\x0bLockMuscles\x12\x16.google.protobuf.Empty\x1a .clone.data_types.ServerResponse\x12Y\n\x0cSetPressures\x12\'.clone.data_types.MusclePressureSetting\x1a .clone.data_types.ServerResponse\x12N\n\tGetConfig\x12\x16.google.protobuf.Empty\x1a).clone.controller.ControllerRuntimeConfig\x12S\n\tGetValves\x12!.clone.data_types.GetNodesRequest\x1a#.clone.controller.ValveListResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'clone_client.controller.proto.controller_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_CONTROLLERRUNTIMECONFIG']._serialized_start=134
  _globals['_CONTROLLERRUNTIMECONFIG']._serialized_end=239
  _globals['_VALVELISTRESPONSE']._serialized_start=241
  _globals['_VALVELISTRESPONSE']._serialized_end=368
  _globals['_WATERPUMPINFO']._serialized_start=370
  _globals['_WATERPUMPINFO']._serialized_end=489
  _globals['_WATERPUMPINFORESPONSE']._serialized_start=491
  _globals['_WATERPUMPINFORESPONSE']._serialized_end=613
  _globals['_CONTROLLERGRPC']._serialized_start=616
  _globals['_CONTROLLERGRPC']._serialized_end=1448
# @@protoc_insertion_point(module_scope)