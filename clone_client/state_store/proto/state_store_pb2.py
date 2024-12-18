# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: clone_client/state_store/proto/state_store.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'clone_client/state_store/proto/state_store.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from clone_client.proto import data_types_pb2 as clone__client_dot_proto_dot_data__types__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n0clone_client/state_store/proto/state_store.proto\x12\x11\x63lone.state_store\x1a\x1bgoogle/protobuf/empty.proto\x1a#clone_client/proto/data_types.proto\"j\n\x07IMUData\x12\x0f\n\x07node_id\x18\x01 \x01(\r\x12\t\n\x01w\x18\x02 \x01(\x02\x12\t\n\x01x\x18\x03 \x01(\x02\x12\t\n\x01y\x18\x04 \x01(\x02\x12\t\n\x01z\x18\x05 \x01(\x02\x12\n\n\x02\x61x\x18\x06 \x01(\x02\x12\n\n\x02\x61y\x18\x07 \x01(\x02\x12\n\n\x02\x61z\x18\x08 \x01(\x02\"K\n\rTelemetryData\x12\x11\n\tpressures\x18\x01 \x03(\x02\x12\'\n\x03imu\x18\x02 \x03(\x0b\x32\x1a.clone.state_store.IMUData\"\x80\x01\n\x15TelemetryDataResponse\x12.\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32 .clone.state_store.TelemetryData\x12\x37\n\rresponse_data\x18\x02 \x01(\x0b\x32 .clone.data_types.ServerResponse\"5\n\x19PressureSensorCalibration\x12\x0b\n\x03min\x18\x01 \x01(\x05\x12\x0b\n\x03max\x18\x02 \x01(\x05\"Y\n\x0f\x43\x61librationData\x12\x46\n\x10pressure_sensors\x18\x01 \x03(\x0b\x32,.clone.state_store.PressureSensorCalibration\"@\n\x0fImuMappingModel\x12\x0f\n\x07node_id\x18\x01 \x01(\r\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0e\n\x06parent\x18\x03 \x01(\r\"\xa7\x02\n\nSystemInfo\x12;\n\x07muscles\x18\x02 \x03(\x0b\x32*.clone.state_store.SystemInfo.MusclesEntry\x12\x30\n\x04imus\x18\x03 \x03(\x0b\x32\".clone.state_store.ImuMappingModel\x12<\n\x10\x63\x61libration_data\x18\x04 \x01(\x0b\x32\".clone.state_store.CalibrationData\x12<\n\x10telemetry_config\x18\x05 \x01(\x0e\x32\".clone.state_store.TelemetryConfig\x1a.\n\x0cMusclesEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"u\n\x12SystemInfoResponse\x12+\n\x04info\x18\x01 \x01(\x0b\x32\x1d.clone.state_store.SystemInfo\x12\x32\n\x08response\x18\x02 \x01(\x0b\x32 .clone.data_types.ServerResponse*1\n\x0fTelemetryConfig\x12\x0c\n\x08PRESSURE\x10\x00\x12\x07\n\x03IMU\x10\x01\x12\x07\n\x03\x41LL\x10\x02\x32\xcc\x02\n\x16StateStoreReceiverGRPC\x12X\n\x12SubscribeTelemetry\x12\x16.google.protobuf.Empty\x1a(.clone.state_store.TelemetryDataResponse0\x01\x12P\n\x0cGetTelemetry\x12\x16.google.protobuf.Empty\x1a(.clone.state_store.TelemetryDataResponse\x12N\n\rGetSystemInfo\x12\x16.google.protobuf.Empty\x1a%.clone.state_store.SystemInfoResponse\x12\x36\n\x04Ping\x12\x16.google.protobuf.Empty\x1a\x16.google.protobuf.Emptyb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'clone_client.state_store.proto.state_store_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_SYSTEMINFO_MUSCLESENTRY']._loaded_options = None
  _globals['_SYSTEMINFO_MUSCLESENTRY']._serialized_options = b'8\001'
  _globals['_TELEMETRYCONFIG']._serialized_start=1082
  _globals['_TELEMETRYCONFIG']._serialized_end=1131
  _globals['_IMUDATA']._serialized_start=137
  _globals['_IMUDATA']._serialized_end=243
  _globals['_TELEMETRYDATA']._serialized_start=245
  _globals['_TELEMETRYDATA']._serialized_end=320
  _globals['_TELEMETRYDATARESPONSE']._serialized_start=323
  _globals['_TELEMETRYDATARESPONSE']._serialized_end=451
  _globals['_PRESSURESENSORCALIBRATION']._serialized_start=453
  _globals['_PRESSURESENSORCALIBRATION']._serialized_end=506
  _globals['_CALIBRATIONDATA']._serialized_start=508
  _globals['_CALIBRATIONDATA']._serialized_end=597
  _globals['_IMUMAPPINGMODEL']._serialized_start=599
  _globals['_IMUMAPPINGMODEL']._serialized_end=663
  _globals['_SYSTEMINFO']._serialized_start=666
  _globals['_SYSTEMINFO']._serialized_end=961
  _globals['_SYSTEMINFO_MUSCLESENTRY']._serialized_start=915
  _globals['_SYSTEMINFO_MUSCLESENTRY']._serialized_end=961
  _globals['_SYSTEMINFORESPONSE']._serialized_start=963
  _globals['_SYSTEMINFORESPONSE']._serialized_end=1080
  _globals['_STATESTORERECEIVERGRPC']._serialized_start=1134
  _globals['_STATESTORERECEIVERGRPC']._serialized_end=1466
# @@protoc_insertion_point(module_scope)
