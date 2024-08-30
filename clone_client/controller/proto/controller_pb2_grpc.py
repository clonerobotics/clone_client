# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from clone_client.controller.proto import controller_pb2 as clone__client_dot_controller_dot_proto_dot_controller__pb2
from clone_client.proto import data_types_pb2 as clone__client_dot_proto_dot_data__types__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

GRPC_GENERATED_VERSION = '1.65.5'
GRPC_VERSION = grpc.__version__
EXPECTED_ERROR_RELEASE = '1.66.0'
SCHEDULED_RELEASE_DATE = 'August 6, 2024'
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    warnings.warn(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in clone_client/controller/proto/controller_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
        + f' This warning will become an error in {EXPECTED_ERROR_RELEASE},'
        + f' scheduled for release on {SCHEDULED_RELEASE_DATE}.',
        RuntimeWarning
    )


class ControllerGRPCStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SetImpulses = channel.unary_unary(
                '/clone.controller.ControllerGRPC/SetImpulses',
                request_serializer=clone__client_dot_controller_dot_proto_dot_controller__pb2.SetImpulsesMessage.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.SetPulses = channel.unary_unary(
                '/clone.controller.ControllerGRPC/SetPulses',
                request_serializer=clone__client_dot_controller_dot_proto_dot_controller__pb2.SetPulsesMessage.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.SetPressures = channel.unary_unary(
                '/clone.controller.ControllerGRPC/SetPressures',
                request_serializer=clone__client_dot_controller_dot_proto_dot_controller__pb2.SetPressuresMessage.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.LooseMuscles = channel.unary_unary(
                '/clone.controller.ControllerGRPC/LooseMuscles',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.LockMuscles = channel.unary_unary(
                '/clone.controller.ControllerGRPC/LockMuscles',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.StreamSetPressures = channel.stream_unary(
                '/clone.controller.ControllerGRPC/StreamSetPressures',
                request_serializer=clone__client_dot_controller_dot_proto_dot_controller__pb2.SetPressuresMessage.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.GetWaterPumpInfo = channel.unary_unary(
                '/clone.controller.ControllerGRPC/GetWaterPumpInfo',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=clone__client_dot_controller_dot_proto_dot_controller__pb2.WaterPumpInfoResponse.FromString,
                _registered_method=True)
        self.StartWaterPump = channel.unary_unary(
                '/clone.controller.ControllerGRPC/StartWaterPump',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.StopWaterPump = channel.unary_unary(
                '/clone.controller.ControllerGRPC/StopWaterPump',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.SetWaterPumpPressure = channel.unary_unary(
                '/clone.controller.ControllerGRPC/SetWaterPumpPressure',
                request_serializer=clone__client_dot_controller_dot_proto_dot_controller__pb2.WaterPumpPressure.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.GetConfig = channel.unary_unary(
                '/clone.controller.ControllerGRPC/GetConfig',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=clone__client_dot_controller_dot_proto_dot_controller__pb2.ControllerRuntimeConfig.FromString,
                _registered_method=True)


class ControllerGRPCServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SetImpulses(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetPulses(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetPressures(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def LooseMuscles(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def LockMuscles(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StreamSetPressures(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetWaterPumpInfo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StartWaterPump(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StopWaterPump(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetWaterPumpPressure(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetConfig(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ControllerGRPCServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SetImpulses': grpc.unary_unary_rpc_method_handler(
                    servicer.SetImpulses,
                    request_deserializer=clone__client_dot_controller_dot_proto_dot_controller__pb2.SetImpulsesMessage.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'SetPulses': grpc.unary_unary_rpc_method_handler(
                    servicer.SetPulses,
                    request_deserializer=clone__client_dot_controller_dot_proto_dot_controller__pb2.SetPulsesMessage.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'SetPressures': grpc.unary_unary_rpc_method_handler(
                    servicer.SetPressures,
                    request_deserializer=clone__client_dot_controller_dot_proto_dot_controller__pb2.SetPressuresMessage.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'LooseMuscles': grpc.unary_unary_rpc_method_handler(
                    servicer.LooseMuscles,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'LockMuscles': grpc.unary_unary_rpc_method_handler(
                    servicer.LockMuscles,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'StreamSetPressures': grpc.stream_unary_rpc_method_handler(
                    servicer.StreamSetPressures,
                    request_deserializer=clone__client_dot_controller_dot_proto_dot_controller__pb2.SetPressuresMessage.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'GetWaterPumpInfo': grpc.unary_unary_rpc_method_handler(
                    servicer.GetWaterPumpInfo,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=clone__client_dot_controller_dot_proto_dot_controller__pb2.WaterPumpInfoResponse.SerializeToString,
            ),
            'StartWaterPump': grpc.unary_unary_rpc_method_handler(
                    servicer.StartWaterPump,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'StopWaterPump': grpc.unary_unary_rpc_method_handler(
                    servicer.StopWaterPump,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'SetWaterPumpPressure': grpc.unary_unary_rpc_method_handler(
                    servicer.SetWaterPumpPressure,
                    request_deserializer=clone__client_dot_controller_dot_proto_dot_controller__pb2.WaterPumpPressure.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'GetConfig': grpc.unary_unary_rpc_method_handler(
                    servicer.GetConfig,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=clone__client_dot_controller_dot_proto_dot_controller__pb2.ControllerRuntimeConfig.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'clone.controller.ControllerGRPC', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('clone.controller.ControllerGRPC', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ControllerGRPC(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SetImpulses(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/clone.controller.ControllerGRPC/SetImpulses',
            clone__client_dot_controller_dot_proto_dot_controller__pb2.SetImpulsesMessage.SerializeToString,
            clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SetPulses(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/clone.controller.ControllerGRPC/SetPulses',
            clone__client_dot_controller_dot_proto_dot_controller__pb2.SetPulsesMessage.SerializeToString,
            clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SetPressures(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/clone.controller.ControllerGRPC/SetPressures',
            clone__client_dot_controller_dot_proto_dot_controller__pb2.SetPressuresMessage.SerializeToString,
            clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def LooseMuscles(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/clone.controller.ControllerGRPC/LooseMuscles',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def LockMuscles(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/clone.controller.ControllerGRPC/LockMuscles',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def StreamSetPressures(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_unary(
            request_iterator,
            target,
            '/clone.controller.ControllerGRPC/StreamSetPressures',
            clone__client_dot_controller_dot_proto_dot_controller__pb2.SetPressuresMessage.SerializeToString,
            clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetWaterPumpInfo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/clone.controller.ControllerGRPC/GetWaterPumpInfo',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            clone__client_dot_controller_dot_proto_dot_controller__pb2.WaterPumpInfoResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def StartWaterPump(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/clone.controller.ControllerGRPC/StartWaterPump',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def StopWaterPump(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/clone.controller.ControllerGRPC/StopWaterPump',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SetWaterPumpPressure(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/clone.controller.ControllerGRPC/SetWaterPumpPressure',
            clone__client_dot_controller_dot_proto_dot_controller__pb2.WaterPumpPressure.SerializeToString,
            clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetConfig(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/clone.controller.ControllerGRPC/GetConfig',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            clone__client_dot_controller_dot_proto_dot_controller__pb2.ControllerRuntimeConfig.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
