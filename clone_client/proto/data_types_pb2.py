# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: clone_client/proto/data_types.proto
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
    'clone_client/proto/data_types.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n#clone_client/proto/data_types.proto\x12\x10\x63lone.data_types\"g\n\tErrorInfo\x12*\n\x05\x65rror\x18\x01 \x01(\x0e\x32\x1b.clone.data_types.ErrorType\x12\x0c\n\x04info\x18\x02 \x01(\t\x12\x14\n\x07subtype\x18\x03 \x01(\rH\x00\x88\x01\x01\x42\n\n\x08_subtype\"\\\n\x0eServerResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12/\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x1b.clone.data_types.ErrorInfoH\x00\x88\x01\x01\x42\x08\n\x06_error*X\n\tErrorType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x0f\n\x0bGOLEM_ERROR\x10\x01\x12\x11\n\rWRONG_REQUEST\x10\x02\x12\x1a\n\x16\x44ISABLED_FUNCTIONALITY\x10\x03\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'clone_client.proto.data_types_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_ERRORTYPE']._serialized_start=256
  _globals['_ERRORTYPE']._serialized_end=344
  _globals['_ERRORINFO']._serialized_start=57
  _globals['_ERRORINFO']._serialized_end=160
  _globals['_SERVERRESPONSE']._serialized_start=162
  _globals['_SERVERRESPONSE']._serialized_end=254
# @@protoc_insertion_point(module_scope)
