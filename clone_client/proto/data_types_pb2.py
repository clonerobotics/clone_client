# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: clone_client/proto/data_types.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n#clone_client/proto/data_types.proto\x12\x10\x63lone.data_types\x1a\x1fgoogle/protobuf/timestamp.proto\"}\n\nPulseValue\x12.\n\tctrl_type\x18\x01 \x01(\x0e\x32\x1b.clone.data_types.PulseType\x12\x14\n\x0cpulse_len_ms\x18\x02 \x01(\x02\x12\x14\n\x0c\x64\x65lay_len_ms\x18\x03 \x01(\x02\x12\x13\n\x0b\x64uration_ms\x18\x04 \x01(\x02\"P\n\x05Pulse\x12-\n\x05value\x18\x01 \x01(\x0b\x32\x1c.clone.data_types.PulseValueH\x00\x12\x10\n\x06ignore\x18\x02 \x01(\x08H\x00\x42\x06\n\x04\x64\x61ta\"6\n\x0bMusclePulse\x12\'\n\x06pulses\x18\x02 \x03(\x0b\x32\x17.clone.data_types.Pulse\"5\n\x08Movement\x12\x0f\n\x05value\x18\x01 \x01(\x02H\x00\x12\x10\n\x06ignore\x18\x02 \x01(\x08H\x00\x42\x06\n\x04\x64\x61ta\"E\n\x0eMuscleMovement\x12-\n\tmovements\x18\x02 \x03(\x0b\x32\x1a.clone.data_types.MovementJ\x04\x08\x01\x10\x02\"0\n\x15MusclePressureSetting\x12\x11\n\tpressures\x18\x02 \x03(\x02J\x04\x08\x01\x10\x02\"X\n\x14MusclePressuresState\x12-\n\ttimestamp\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x11\n\tpressures\x18\x02 \x03(\x02\"E\n\tErrorInfo\x12*\n\x05\x65rror\x18\x01 \x01(\x0e\x32\x1b.clone.data_types.ErrorType\x12\x0c\n\x04info\x18\x02 \x01(\t\"\\\n\x0eServerResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12/\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x1b.clone.data_types.ErrorInfoH\x00\x88\x01\x01\x42\x08\n\x06_error\"\x1a\n\x08NodeList\x12\x0e\n\x06values\x18\x01 \x03(\r\"\x81\x01\n\x10MusclesValveInfo\x12>\n\x06values\x18\x01 \x03(\x0b\x32..clone.data_types.MusclesValveInfo.ValuesEntry\x1a-\n\x0bValuesEntry\x12\x0b\n\x03key\x18\x01 \x01(\r\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"%\n\x0fGetNodesRequest\x12\x12\n\nrediscover\x18\x01 \x01(\x08\"%\n\x11WaterPumpPressure\x12\x10\n\x08pressure\x18\x01 \x01(\x02*\x93\x01\n\tErrorType\x12\x17\n\x13UNSUPPORTED_REQUEST\x10\x00\x12\x0f\n\x0bINSTRUCTION\x10\x01\x12\x18\n\x14INVALID_SERVER_STATE\x10\x02\x12\x0f\n\x0b\x41\x43QUISITION\x10\x03\x12\x0b\n\x07UNKNOWN\x10\x04\x12\x0f\n\x0bRPC_TIMEOUT\x10\x05\x12\x13\n\x0fSERVICE_TIMEOUT\x10\x06*\x1c\n\tPulseType\x12\x06\n\x02IN\x10\x00\x12\x07\n\x03OUT\x10\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'clone_client.proto.data_types_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_MUSCLESVALVEINFO_VALUESENTRY']._options = None
  _globals['_MUSCLESVALVEINFO_VALUESENTRY']._serialized_options = b'8\001'
  _globals['_ERRORTYPE']._serialized_start=1025
  _globals['_ERRORTYPE']._serialized_end=1172
  _globals['_PULSETYPE']._serialized_start=1174
  _globals['_PULSETYPE']._serialized_end=1202
  _globals['_PULSEVALUE']._serialized_start=90
  _globals['_PULSEVALUE']._serialized_end=215
  _globals['_PULSE']._serialized_start=217
  _globals['_PULSE']._serialized_end=297
  _globals['_MUSCLEPULSE']._serialized_start=299
  _globals['_MUSCLEPULSE']._serialized_end=353
  _globals['_MOVEMENT']._serialized_start=355
  _globals['_MOVEMENT']._serialized_end=408
  _globals['_MUSCLEMOVEMENT']._serialized_start=410
  _globals['_MUSCLEMOVEMENT']._serialized_end=479
  _globals['_MUSCLEPRESSURESETTING']._serialized_start=481
  _globals['_MUSCLEPRESSURESETTING']._serialized_end=529
  _globals['_MUSCLEPRESSURESSTATE']._serialized_start=531
  _globals['_MUSCLEPRESSURESSTATE']._serialized_end=619
  _globals['_ERRORINFO']._serialized_start=621
  _globals['_ERRORINFO']._serialized_end=690
  _globals['_SERVERRESPONSE']._serialized_start=692
  _globals['_SERVERRESPONSE']._serialized_end=784
  _globals['_NODELIST']._serialized_start=786
  _globals['_NODELIST']._serialized_end=812
  _globals['_MUSCLESVALVEINFO']._serialized_start=815
  _globals['_MUSCLESVALVEINFO']._serialized_end=944
  _globals['_MUSCLESVALVEINFO_VALUESENTRY']._serialized_start=899
  _globals['_MUSCLESVALVEINFO_VALUESENTRY']._serialized_end=944
  _globals['_GETNODESREQUEST']._serialized_start=946
  _globals['_GETNODESREQUEST']._serialized_end=983
  _globals['_WATERPUMPPRESSURE']._serialized_start=985
  _globals['_WATERPUMPPRESSURE']._serialized_end=1022
# @@protoc_insertion_point(module_scope)
