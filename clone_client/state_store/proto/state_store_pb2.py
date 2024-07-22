# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: clone_client/state_store/proto/state_store.proto
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


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n0clone_client/state_store/proto/state_store.proto\x12\x11\x63lone.state_store\x1a\x1bgoogle/protobuf/empty.proto\x1a#clone_client/proto/data_types.proto\"\x19\n\x06NCount\x12\x0f\n\x07n_count\x18\x01 \x01(\x05\"\x9b\x01\n\x12PublishedPressures\x12>\n\tpressures\x18\x01 \x01(\x0b\x32&.clone.data_types.MusclePressuresStateH\x00\x88\x01\x01\x12\x37\n\rresponse_data\x18\x02 \x01(\x0b\x32 .clone.data_types.ServerResponseB\x0c\n\n_pressures\"\x90\x01\n\x16PublishedPressuresList\x12=\n\rpressure_list\x18\x01 \x03(\x0b\x32&.clone.data_types.MusclePressuresState\x12\x37\n\rresponse_data\x18\x02 \x01(\x0b\x32 .clone.data_types.ServerResponse\"5\n\x19PressureSensorCalibration\x12\x0b\n\x03min\x18\x01 \x01(\r\x12\x0b\n\x03max\x18\x02 \x01(\r\"Y\n\x0f\x43\x61librationData\x12\x46\n\x10pressure_sensors\x18\x01 \x03(\x0b\x32,.clone.state_store.PressureSensorCalibration\"\xb3\x01\n\x08HandInfo\x12\x39\n\x07muscles\x18\x02 \x03(\x0b\x32(.clone.state_store.HandInfo.MusclesEntry\x12<\n\x10\x63\x61libration_data\x18\x03 \x01(\x0b\x32\".clone.state_store.CalibrationData\x1a.\n\x0cMusclesEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"q\n\x10HandInfoResponse\x12)\n\x04info\x18\x01 \x01(\x0b\x32\x1b.clone.state_store.HandInfo\x12\x32\n\x08response\x18\x02 \x01(\x0b\x32 .clone.data_types.ServerResponse2\xe2\x02\n\x13StateStorePublisher\x12U\n\x12SubscribePressures\x12\x16.google.protobuf.Empty\x1a%.clone.state_store.PublishedPressures0\x01\x12M\n\x0cGetPressures\x12\x16.google.protobuf.Empty\x1a%.clone.state_store.PublishedPressures\x12Y\n\x11GetLastNPressures\x12\x19.clone.state_store.NCount\x1a).clone.state_store.PublishedPressuresList\x12J\n\x0bGetHandInfo\x12\x16.google.protobuf.Empty\x1a#.clone.state_store.HandInfoResponse2i\n\nStateStore\x12[\n\x0fUpdatePressures\x12&.clone.data_types.MusclePressuresState\x1a .clone.data_types.ServerResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'clone_client.state_store.proto.state_store_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_HANDINFO_MUSCLESENTRY']._options = None
  _globals['_HANDINFO_MUSCLESENTRY']._serialized_options = b'8\001'
  _globals['_NCOUNT']._serialized_start=137
  _globals['_NCOUNT']._serialized_end=162
  _globals['_PUBLISHEDPRESSURES']._serialized_start=165
  _globals['_PUBLISHEDPRESSURES']._serialized_end=320
  _globals['_PUBLISHEDPRESSURESLIST']._serialized_start=323
  _globals['_PUBLISHEDPRESSURESLIST']._serialized_end=467
  _globals['_PRESSURESENSORCALIBRATION']._serialized_start=469
  _globals['_PRESSURESENSORCALIBRATION']._serialized_end=522
  _globals['_CALIBRATIONDATA']._serialized_start=524
  _globals['_CALIBRATIONDATA']._serialized_end=613
  _globals['_HANDINFO']._serialized_start=616
  _globals['_HANDINFO']._serialized_end=795
  _globals['_HANDINFO_MUSCLESENTRY']._serialized_start=749
  _globals['_HANDINFO_MUSCLESENTRY']._serialized_end=795
  _globals['_HANDINFORESPONSE']._serialized_start=797
  _globals['_HANDINFORESPONSE']._serialized_end=910
  _globals['_STATESTOREPUBLISHER']._serialized_start=913
  _globals['_STATESTOREPUBLISHER']._serialized_end=1267
  _globals['_STATESTORE']._serialized_start=1269
  _globals['_STATESTORE']._serialized_end=1374
# @@protoc_insertion_point(module_scope)
