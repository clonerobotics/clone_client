# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: clone_client/proto/hardware_driver.proto
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
    'clone_client/proto/hardware_driver.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n(clone_client/proto/hardware_driver.proto\x12\x15\x63lone.hardware_driver\"4\n\x11SendDirectMessage\x12\x0f\n\x07node_id\x18\x01 \x01(\r\x12\x0e\n\x06valves\x18\x02 \x01(\r\"\x8a\x01\n\x15SendManyDirectMessage\x12\x44\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32\x36.clone.hardware_driver.SendManyDirectMessage.DataEntry\x1a+\n\tDataEntry\x12\x0b\n\x03key\x18\x01 \x01(\r\x12\r\n\x05value\x18\x02 \x01(\r:\x02\x38\x01\"/\n\x0eImpulseControl\x12\x0e\n\x06valves\x18\x01 \x01(\r\x12\r\n\x05\x64\x65lay\x18\x02 \x01(\r\"]\n\x12SendImpulseMessage\x12\x0f\n\x07node_id\x18\x01 \x01(\r\x12\x36\n\x07\x63ontrol\x18\x02 \x01(\x0b\x32%.clone.hardware_driver.ImpulseControl\"\xb3\x01\n\x16SendManyImpulseMessage\x12\x45\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32\x37.clone.hardware_driver.SendManyImpulseMessage.DataEntry\x1aR\n\tDataEntry\x12\x0b\n\x03key\x18\x01 \x01(\r\x12\x34\n\x05value\x18\x02 \x01(\x0b\x32%.clone.hardware_driver.ImpulseControl:\x02\x38\x01\"v\n\x10SendPulseMessage\x12\x0f\n\x07node_id\x18\x01 \x01(\r\x12\x10\n\x08valve_id\x18\x02 \x01(\r\x12\x14\n\x0cpulse_len_ms\x18\x03 \x01(\r\x12\x14\n\x0c\x64\x65lay_len_ms\x18\x04 \x01(\r\x12\x13\n\x0b\x64uration_ms\x18\x05 \x01(\r\"$\n\x0fPressureControl\x12\x11\n\tpressures\x18\x01 \x03(\x05\"\xb6\x01\n\x17SendManyPressureMessage\x12\x46\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32\x38.clone.hardware_driver.SendManyPressureMessage.DataEntry\x1aS\n\tDataEntry\x12\x0b\n\x03key\x18\x01 \x01(\r\x12\x35\n\x05value\x18\x02 \x01(\x0b\x32&.clone.hardware_driver.PressureControl:\x02\x38\x01\"\xdf\x02\n\x11PinchValveControl\x12\x42\n\x04mode\x18\x01 \x01(\x0e\x32\x34.clone.hardware_driver.PinchValveControl.ControlMode\x12\r\n\x05value\x18\x02 \x01(\x05\"\xb1\x01\n\rPositionsType\x12\x14\n\x10POSITION_UNKNOWN\x10\x00\x12\x0f\n\x0b\x42OTH_CLOSED\x10\x01\x12\x0f\n\x0b\x42OTH_OPENED\x10\x02\x12\x16\n\x12INLET_FULLY_OPENED\x10\x03\x12\x1a\n\x16INLET_PARTIALLY_OPENED\x10\x04\x12\x17\n\x13OUTLET_FULLY_OPENED\x10\x05\x12\x1b\n\x17OUTLET_PARTIALLY_OPENED\x10\x06\"C\n\x0b\x43ontrolMode\x12\x0c\n\x08RESERVED\x10\x00\x12\t\n\x05\x41NGLE\x10\x01\x12\x0c\n\x08PRESSURE\x10\x02\x12\r\n\tPOSITIONS\x10\x03\"j\n\x1cSendPinchValveControlMessage\x12\x0f\n\x07node_id\x18\x01 \x01(\r\x12\x39\n\x07\x63ontrol\x18\x02 \x01(\x0b\x32(.clone.hardware_driver.PinchValveControl\"\xca\x01\n SendManyPinchValveControlMessage\x12O\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32\x41.clone.hardware_driver.SendManyPinchValveControlMessage.DataEntry\x1aU\n\tDataEntry\x12\x0b\n\x03key\x18\x01 \x01(\r\x12\x37\n\x05value\x18\x02 \x01(\x0b\x32(.clone.hardware_driver.PinchValveControl:\x02\x38\x01\"9\n\x0fGetNodesMessage\x12\x17\n\nproduct_id\x18\x02 \x01(\rH\x00\x88\x01\x01\x42\r\n\x0b_product_id\"0\n\tBusDevice\x12\x0f\n\x07node_id\x18\x01 \x01(\r\x12\x12\n\nproduct_id\x18\x02 \x01(\r\";\n\x08NodeList\x12/\n\x05nodes\x18\x01 \x03(\x0b\x32 .clone.hardware_driver.BusDevice\"\x92\x01\n\x07NodeMap\x12\x38\n\x05nodes\x18\x01 \x03(\x0b\x32).clone.hardware_driver.NodeMap.NodesEntry\x1aM\n\nNodesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12.\n\x05value\x18\x02 \x01(\x0b\x32\x1f.clone.hardware_driver.NodeList:\x02\x38\x01\"k\n\x1cSendPinchValveCommandMessage\x12\x0f\n\x07node_id\x18\x01 \x01(\r\x12:\n\x07\x63ommand\x18\x02 \x01(\x0e\x32).clone.hardware_driver.PinchValveCommands\"\xd7\x01\n SendManyPinchValveCommandMessage\x12W\n\x08\x63ommands\x18\x01 \x03(\x0b\x32\x45.clone.hardware_driver.SendManyPinchValveCommandMessage.CommandsEntry\x1aZ\n\rCommandsEntry\x12\x0b\n\x03key\x18\x01 \x01(\r\x12\x38\n\x05value\x18\x02 \x01(\x0e\x32).clone.hardware_driver.PinchValveCommands:\x02\x38\x01*\x90\x01\n\x12PinchValveCommands\x12\x0c\n\x08RESERVED\x10\x00\x12\x19\n\x15\x45NABLE_STEPPER_DRIVER\x10\x01\x12\x1a\n\x16\x44ISABLE_STEPPER_DRIVER\x10\x02\x12\x19\n\x15\x45NABLE_STEPPER_VBOOST\x10\x03\x12\x1a\n\x16\x44ISABLE_STEPPER_VBOOST\x10\x04\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'clone_client.proto.hardware_driver_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_SENDMANYDIRECTMESSAGE_DATAENTRY']._loaded_options = None
  _globals['_SENDMANYDIRECTMESSAGE_DATAENTRY']._serialized_options = b'8\001'
  _globals['_SENDMANYIMPULSEMESSAGE_DATAENTRY']._loaded_options = None
  _globals['_SENDMANYIMPULSEMESSAGE_DATAENTRY']._serialized_options = b'8\001'
  _globals['_SENDMANYPRESSUREMESSAGE_DATAENTRY']._loaded_options = None
  _globals['_SENDMANYPRESSUREMESSAGE_DATAENTRY']._serialized_options = b'8\001'
  _globals['_SENDMANYPINCHVALVECONTROLMESSAGE_DATAENTRY']._loaded_options = None
  _globals['_SENDMANYPINCHVALVECONTROLMESSAGE_DATAENTRY']._serialized_options = b'8\001'
  _globals['_NODEMAP_NODESENTRY']._loaded_options = None
  _globals['_NODEMAP_NODESENTRY']._serialized_options = b'8\001'
  _globals['_SENDMANYPINCHVALVECOMMANDMESSAGE_COMMANDSENTRY']._loaded_options = None
  _globals['_SENDMANYPINCHVALVECOMMANDMESSAGE_COMMANDSENTRY']._serialized_options = b'8\001'
  _globals['_PINCHVALVECOMMANDS']._serialized_start=2245
  _globals['_PINCHVALVECOMMANDS']._serialized_end=2389
  _globals['_SENDDIRECTMESSAGE']._serialized_start=67
  _globals['_SENDDIRECTMESSAGE']._serialized_end=119
  _globals['_SENDMANYDIRECTMESSAGE']._serialized_start=122
  _globals['_SENDMANYDIRECTMESSAGE']._serialized_end=260
  _globals['_SENDMANYDIRECTMESSAGE_DATAENTRY']._serialized_start=217
  _globals['_SENDMANYDIRECTMESSAGE_DATAENTRY']._serialized_end=260
  _globals['_IMPULSECONTROL']._serialized_start=262
  _globals['_IMPULSECONTROL']._serialized_end=309
  _globals['_SENDIMPULSEMESSAGE']._serialized_start=311
  _globals['_SENDIMPULSEMESSAGE']._serialized_end=404
  _globals['_SENDMANYIMPULSEMESSAGE']._serialized_start=407
  _globals['_SENDMANYIMPULSEMESSAGE']._serialized_end=586
  _globals['_SENDMANYIMPULSEMESSAGE_DATAENTRY']._serialized_start=504
  _globals['_SENDMANYIMPULSEMESSAGE_DATAENTRY']._serialized_end=586
  _globals['_SENDPULSEMESSAGE']._serialized_start=588
  _globals['_SENDPULSEMESSAGE']._serialized_end=706
  _globals['_PRESSURECONTROL']._serialized_start=708
  _globals['_PRESSURECONTROL']._serialized_end=744
  _globals['_SENDMANYPRESSUREMESSAGE']._serialized_start=747
  _globals['_SENDMANYPRESSUREMESSAGE']._serialized_end=929
  _globals['_SENDMANYPRESSUREMESSAGE_DATAENTRY']._serialized_start=846
  _globals['_SENDMANYPRESSUREMESSAGE_DATAENTRY']._serialized_end=929
  _globals['_PINCHVALVECONTROL']._serialized_start=932
  _globals['_PINCHVALVECONTROL']._serialized_end=1283
  _globals['_PINCHVALVECONTROL_POSITIONSTYPE']._serialized_start=1037
  _globals['_PINCHVALVECONTROL_POSITIONSTYPE']._serialized_end=1214
  _globals['_PINCHVALVECONTROL_CONTROLMODE']._serialized_start=1216
  _globals['_PINCHVALVECONTROL_CONTROLMODE']._serialized_end=1283
  _globals['_SENDPINCHVALVECONTROLMESSAGE']._serialized_start=1285
  _globals['_SENDPINCHVALVECONTROLMESSAGE']._serialized_end=1391
  _globals['_SENDMANYPINCHVALVECONTROLMESSAGE']._serialized_start=1394
  _globals['_SENDMANYPINCHVALVECONTROLMESSAGE']._serialized_end=1596
  _globals['_SENDMANYPINCHVALVECONTROLMESSAGE_DATAENTRY']._serialized_start=1511
  _globals['_SENDMANYPINCHVALVECONTROLMESSAGE_DATAENTRY']._serialized_end=1596
  _globals['_GETNODESMESSAGE']._serialized_start=1598
  _globals['_GETNODESMESSAGE']._serialized_end=1655
  _globals['_BUSDEVICE']._serialized_start=1657
  _globals['_BUSDEVICE']._serialized_end=1705
  _globals['_NODELIST']._serialized_start=1707
  _globals['_NODELIST']._serialized_end=1766
  _globals['_NODEMAP']._serialized_start=1769
  _globals['_NODEMAP']._serialized_end=1915
  _globals['_NODEMAP_NODESENTRY']._serialized_start=1838
  _globals['_NODEMAP_NODESENTRY']._serialized_end=1915
  _globals['_SENDPINCHVALVECOMMANDMESSAGE']._serialized_start=1917
  _globals['_SENDPINCHVALVECOMMANDMESSAGE']._serialized_end=2024
  _globals['_SENDMANYPINCHVALVECOMMANDMESSAGE']._serialized_start=2027
  _globals['_SENDMANYPINCHVALVECOMMANDMESSAGE']._serialized_end=2242
  _globals['_SENDMANYPINCHVALVECOMMANDMESSAGE_COMMANDSENTRY']._serialized_start=2152
  _globals['_SENDMANYPINCHVALVECOMMANDMESSAGE_COMMANDSENTRY']._serialized_end=2242
# @@protoc_insertion_point(module_scope)
