# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: clone_client/proto/data_types.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n#clone_client/proto/data_types.proto\x12\x12\x63lonepb.data_types\x1a\x1fgoogle/protobuf/timestamp.proto\")\n\x0eMuscleMovement\x12\x11\n\tmovements\x18\x02 \x03(\x02J\x04\x08\x01\x10\x02\"0\n\x15MusclePressureSetting\x12\x11\n\tpressures\x18\x02 \x03(\x02J\x04\x08\x01\x10\x02\"X\n\x14MusclePressuresState\x12-\n\ttimestamp\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x11\n\tpressures\x18\x02 \x03(\x02\"G\n\tErrorInfo\x12,\n\x05\x65rror\x18\x01 \x01(\x0e\x32\x1d.clonepb.data_types.ErrorType\x12\x0c\n\x04info\x18\x02 \x01(\t\"^\n\x0eServerResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x31\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x1d.clonepb.data_types.ErrorInfoH\x00\x88\x01\x01\x42\x08\n\x06_error\"\x1a\n\x08NodeList\x12\x0e\n\x06values\x18\x01 \x03(\r\"\x83\x01\n\x10MusclesValveInfo\x12@\n\x06values\x18\x01 \x03(\x0b\x32\x30.clonepb.data_types.MusclesValveInfo.ValuesEntry\x1a-\n\x0bValuesEntry\x12\x0b\n\x03key\x18\x01 \x01(\r\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"%\n\x0fGetNodesRequest\x12\x12\n\nrediscover\x18\x01 \x01(\x08\"\'\n\x13PressureGenPressure\x12\x10\n\x08pressure\x18\x01 \x01(\x02*\x93\x01\n\tErrorType\x12\x17\n\x13UNSUPPORTED_REQUEST\x10\x00\x12\x0f\n\x0bINSTRUCTION\x10\x01\x12\x18\n\x14INVALID_SERVER_STATE\x10\x02\x12\x0f\n\x0b\x41\x43QUISITION\x10\x03\x12\x0b\n\x07UNKNOWN\x10\x04\x12\x0f\n\x0bRPC_TIMEOUT\x10\x05\x12\x13\n\x0fSERVICE_TIMEOUT\x10\x06\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'clone_client.proto.data_types_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _MUSCLESVALVEINFO_VALUESENTRY._options = None
  _MUSCLESVALVEINFO_VALUESENTRY._serialized_options = b'8\001'
  _globals['_ERRORTYPE']._serialized_start=687
  _globals['_ERRORTYPE']._serialized_end=834
  _globals['_MUSCLEMOVEMENT']._serialized_start=92
  _globals['_MUSCLEMOVEMENT']._serialized_end=133
  _globals['_MUSCLEPRESSURESETTING']._serialized_start=135
  _globals['_MUSCLEPRESSURESETTING']._serialized_end=183
  _globals['_MUSCLEPRESSURESSTATE']._serialized_start=185
  _globals['_MUSCLEPRESSURESSTATE']._serialized_end=273
  _globals['_ERRORINFO']._serialized_start=275
  _globals['_ERRORINFO']._serialized_end=346
  _globals['_SERVERRESPONSE']._serialized_start=348
  _globals['_SERVERRESPONSE']._serialized_end=442
  _globals['_NODELIST']._serialized_start=444
  _globals['_NODELIST']._serialized_end=470
  _globals['_MUSCLESVALVEINFO']._serialized_start=473
  _globals['_MUSCLESVALVEINFO']._serialized_end=604
  _globals['_MUSCLESVALVEINFO_VALUESENTRY']._serialized_start=559
  _globals['_MUSCLESVALVEINFO_VALUESENTRY']._serialized_end=604
  _globals['_GETNODESREQUEST']._serialized_start=606
  _globals['_GETNODESREQUEST']._serialized_end=643
  _globals['_PRESSUREGENPRESSURE']._serialized_start=645
  _globals['_PRESSUREGENPRESSURE']._serialized_end=684
# @@protoc_insertion_point(module_scope)
