# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: clone_client/proto/state_store.proto
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
    'clone_client/proto/state_store.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from clone_client.proto import data_types_pb2 as clone__client_dot_proto_dot_data__types__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n$clone_client/proto/state_store.proto\x12\x11\x63lone.state_store\x1a\x1bgoogle/protobuf/empty.proto\x1a#clone_client/proto/data_types.proto\"[\n\x12PoseVectorResponse\x12\x0c\n\x04qpos\x18\x01 \x03(\x01\x12\x37\n\rresponse_data\x18\x02 \x01(\x0b\x32 .clone.data_types.ServerResponse\"j\n\x07IMUData\x12\x0f\n\x07node_id\x18\x01 \x01(\r\x12\t\n\x01w\x18\x02 \x01(\x02\x12\t\n\x01x\x18\x03 \x01(\x02\x12\t\n\x01y\x18\x04 \x01(\x02\x12\t\n\x01z\x18\x05 \x01(\x02\x12\n\n\x02\x61x\x18\x06 \x01(\x02\x12\n\n\x02\x61y\x18\x07 \x01(\x02\x12\n\n\x02\x61z\x18\x08 \x01(\x02\"\x98\x01\n\x0eMagneticSensor\x12?\n\x06pixels\x18\x01 \x03(\x0b\x32/.clone.state_store.MagneticSensor.MagneticPixel\x12\x13\n\x0btemperature\x18\x05 \x01(\x05\x1a\x30\n\rMagneticPixel\x12\t\n\x01x\x18\x01 \x01(\x05\x12\t\n\x01y\x18\x02 \x01(\x05\x12\t\n\x01z\x18\x03 \x01(\x05\"U\n\x0eMagneticHubRaw\x12\x0f\n\x07node_id\x18\x01 \x01(\r\x12\x32\n\x07sensors\x18\x02 \x03(\x0b\x32!.clone.state_store.MagneticSensor\"S\n\rGaussRiderRaw\x12\x0f\n\x07node_id\x18\x01 \x01(\r\x12\x31\n\x06sensor\x18\x02 \x01(\x0b\x32!.clone.state_store.MagneticSensor\"\xc1\x01\n\rTelemetryData\x12\x11\n\tpressures\x18\x01 \x03(\x02\x12\'\n\x03rot\x18\x02 \x03(\x0b\x32\x1a.clone.state_store.IMUData\x12\x38\n\rmagnetic_data\x18\x03 \x03(\x0b\x32!.clone.state_store.MagneticHubRaw\x12:\n\x10gauss_rider_data\x18\x04 \x03(\x0b\x32 .clone.state_store.GaussRiderRaw\"\x80\x01\n\x15TelemetryDataResponse\x12.\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32 .clone.state_store.TelemetryData\x12\x37\n\rresponse_data\x18\x02 \x01(\x0b\x32 .clone.data_types.ServerResponse\"5\n\x19PressureSensorCalibration\x12\x0b\n\x03min\x18\x01 \x01(\x05\x12\x0b\n\x03max\x18\x02 \x01(\x05\"Y\n\x0f\x43\x61librationData\x12\x46\n\x10pressure_sensors\x18\x01 \x03(\x0b\x32,.clone.state_store.PressureSensorCalibration\"@\n\x0fImuMappingModel\x12\x0f\n\x07node_id\x18\x01 \x01(\r\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0e\n\x06parent\x18\x03 \x01(\r\"8\n\nQuaternion\x12\t\n\x01w\x18\x01 \x01(\x01\x12\t\n\x01x\x18\x02 \x01(\x01\x12\t\n\x01y\x18\x03 \x01(\x01\x12\t\n\x01z\x18\x04 \x01(\x01\"\xaa\x02\n\x05Joint\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x12\n\nbone_child\x18\x02 \x01(\t\x12\x13\n\x0b\x62one_parent\x18\x03 \x01(\t\x12+\n\x05jtype\x18\x04 \x01(\x0e\x32\x1c.clone.state_store.JointType\x12\x14\n\x0cimu_id_child\x18\x05 \x01(\x05\x12\x15\n\rimu_id_parent\x18\x06 \x01(\x05\x12\x36\n\x0fr_imu2jnt_child\x18\x07 \x01(\x0b\x32\x1d.clone.state_store.Quaternion\x12\x37\n\x10r_imu2jnt_parent\x18\x08 \x01(\x0b\x32\x1d.clone.state_store.Quaternion\x12\x0f\n\x07qpos_nr\x18\t \x01(\x05\x12\x0e\n\x06jnt_nr\x18\n \x01(\x05\"\x8b\x03\n\nSystemInfo\x12;\n\x07muscles\x18\x02 \x03(\x0b\x32*.clone.state_store.SystemInfo.MusclesEntry\x12<\n\x10\x63\x61libration_data\x18\x04 \x01(\x0b\x32\".clone.state_store.CalibrationData\x12<\n\x10telemetry_config\x18\x05 \x01(\x0e\x32\".clone.state_store.TelemetryConfig\x12(\n\x06joints\x18\x06 \x03(\x0b\x32\x18.clone.state_store.Joint\x1a@\n\nMuscleInfo\x12\r\n\x05index\x18\x01 \x01(\r\x12\x0f\n\x07node_id\x18\x02 \x01(\r\x12\x12\n\nchannel_id\x18\x03 \x01(\r\x1aX\n\x0cMusclesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x37\n\x05value\x18\x02 \x01(\x0b\x32(.clone.state_store.SystemInfo.MuscleInfo:\x02\x38\x01\"u\n\x12SystemInfoResponse\x12+\n\x04info\x18\x01 \x01(\x0b\x32\x1d.clone.state_store.SystemInfo\x12\x32\n\x08response\x18\x02 \x01(\x0b\x32 .clone.data_types.ServerResponse*1\n\x0fTelemetryConfig\x12\x0c\n\x08PRESSURE\x10\x00\x12\x07\n\x03IMU\x10\x01\x12\x07\n\x03\x41LL\x10\x02*\x1f\n\tJointType\x12\x08\n\x04\x44OF1\x10\x00\x12\x08\n\x04\x44OF3\x10\x01\x32\xa4\x03\n\x16StateStoreReceiverGRPC\x12X\n\x12SubscribeTelemetry\x12\x16.google.protobuf.Empty\x1a(.clone.state_store.TelemetryDataResponse0\x01\x12P\n\x0cGetTelemetry\x12\x16.google.protobuf.Empty\x1a(.clone.state_store.TelemetryDataResponse\x12N\n\rGetSystemInfo\x12\x16.google.protobuf.Empty\x1a%.clone.state_store.SystemInfoResponse\x12\x36\n\x04Ping\x12\x16.google.protobuf.Empty\x1a\x16.google.protobuf.Empty\x12V\n\x13SubscribePoseVector\x12\x16.google.protobuf.Empty\x1a%.clone.state_store.PoseVectorResponse0\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'clone_client.proto.state_store_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_SYSTEMINFO_MUSCLESENTRY']._loaded_options = None
  _globals['_SYSTEMINFO_MUSCLESENTRY']._serialized_options = b'8\001'
  _globals['_TELEMETRYCONFIG']._serialized_start=2068
  _globals['_TELEMETRYCONFIG']._serialized_end=2117
  _globals['_JOINTTYPE']._serialized_start=2119
  _globals['_JOINTTYPE']._serialized_end=2150
  _globals['_POSEVECTORRESPONSE']._serialized_start=125
  _globals['_POSEVECTORRESPONSE']._serialized_end=216
  _globals['_IMUDATA']._serialized_start=218
  _globals['_IMUDATA']._serialized_end=324
  _globals['_MAGNETICSENSOR']._serialized_start=327
  _globals['_MAGNETICSENSOR']._serialized_end=479
  _globals['_MAGNETICSENSOR_MAGNETICPIXEL']._serialized_start=431
  _globals['_MAGNETICSENSOR_MAGNETICPIXEL']._serialized_end=479
  _globals['_MAGNETICHUBRAW']._serialized_start=481
  _globals['_MAGNETICHUBRAW']._serialized_end=566
  _globals['_GAUSSRIDERRAW']._serialized_start=568
  _globals['_GAUSSRIDERRAW']._serialized_end=651
  _globals['_TELEMETRYDATA']._serialized_start=654
  _globals['_TELEMETRYDATA']._serialized_end=847
  _globals['_TELEMETRYDATARESPONSE']._serialized_start=850
  _globals['_TELEMETRYDATARESPONSE']._serialized_end=978
  _globals['_PRESSURESENSORCALIBRATION']._serialized_start=980
  _globals['_PRESSURESENSORCALIBRATION']._serialized_end=1033
  _globals['_CALIBRATIONDATA']._serialized_start=1035
  _globals['_CALIBRATIONDATA']._serialized_end=1124
  _globals['_IMUMAPPINGMODEL']._serialized_start=1126
  _globals['_IMUMAPPINGMODEL']._serialized_end=1190
  _globals['_QUATERNION']._serialized_start=1192
  _globals['_QUATERNION']._serialized_end=1248
  _globals['_JOINT']._serialized_start=1251
  _globals['_JOINT']._serialized_end=1549
  _globals['_SYSTEMINFO']._serialized_start=1552
  _globals['_SYSTEMINFO']._serialized_end=1947
  _globals['_SYSTEMINFO_MUSCLEINFO']._serialized_start=1793
  _globals['_SYSTEMINFO_MUSCLEINFO']._serialized_end=1857
  _globals['_SYSTEMINFO_MUSCLESENTRY']._serialized_start=1859
  _globals['_SYSTEMINFO_MUSCLESENTRY']._serialized_end=1947
  _globals['_SYSTEMINFORESPONSE']._serialized_start=1949
  _globals['_SYSTEMINFORESPONSE']._serialized_end=2066
  _globals['_STATESTORERECEIVERGRPC']._serialized_start=2153
  _globals['_STATESTORERECEIVERGRPC']._serialized_end=2573
# @@protoc_insertion_point(module_scope)
