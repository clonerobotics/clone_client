# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from clone_client.proto import data_types_pb2 as clone__client_dot_proto_dot_data__types__pb2
from clone_client.valve_driver.proto import valve_driver_pb2 as clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2

GRPC_GENERATED_VERSION = '1.69.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in clone_client/valve_driver/proto/valve_driver_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class ValveDriverGRPCStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendDirect = channel.unary_unary(
                '/clone.valve_driver.ValveDriverGRPC/SendDirect',
                request_serializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendDirectMessage.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.SendManyDirect = channel.unary_unary(
                '/clone.valve_driver.ValveDriverGRPC/SendManyDirect',
                request_serializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyDirectMessage.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.SendImpulse = channel.unary_unary(
                '/clone.valve_driver.ValveDriverGRPC/SendImpulse',
                request_serializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendImpulseMessage.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.SendManyImpulse = channel.unary_unary(
                '/clone.valve_driver.ValveDriverGRPC/SendManyImpulse',
                request_serializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyImpulseMessage.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.SendPulse = channel.unary_unary(
                '/clone.valve_driver.ValveDriverGRPC/SendPulse',
                request_serializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendPulseMessage.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.SendPinchValveControl = channel.unary_unary(
                '/clone.valve_driver.ValveDriverGRPC/SendPinchValveControl',
                request_serializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendPinchValveControlMessage.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.SendManyPinchValveControl = channel.unary_unary(
                '/clone.valve_driver.ValveDriverGRPC/SendManyPinchValveControl',
                request_serializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyPinchValveControlMessage.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.StreamManyPinchValveControl = channel.stream_unary(
                '/clone.valve_driver.ValveDriverGRPC/StreamManyPinchValveControl',
                request_serializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyPinchValveControlMessage.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.SendPinchValveCommand = channel.unary_unary(
                '/clone.valve_driver.ValveDriverGRPC/SendPinchValveCommand',
                request_serializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendPinchValveCommandMessage.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.SendManyPinchValveCommand = channel.unary_unary(
                '/clone.valve_driver.ValveDriverGRPC/SendManyPinchValveCommand',
                request_serializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyPinchValveCommandMessage.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.SendManyPressure = channel.unary_unary(
                '/clone.valve_driver.ValveDriverGRPC/SendManyPressure',
                request_serializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyPressureMessage.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.StreamManyPressure = channel.stream_unary(
                '/clone.valve_driver.ValveDriverGRPC/StreamManyPressure',
                request_serializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyPressureMessage.SerializeToString,
                response_deserializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.FromString,
                _registered_method=True)
        self.GetAllNodes = channel.unary_unary(
                '/clone.valve_driver.ValveDriverGRPC/GetAllNodes',
                request_serializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.GetNodesMessage.SerializeToString,
                response_deserializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.NodeList.FromString,
                _registered_method=True)
        self.GetControllineNodes = channel.unary_unary(
                '/clone.valve_driver.ValveDriverGRPC/GetControllineNodes',
                request_serializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.GetNodesMessage.SerializeToString,
                response_deserializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.NodeList.FromString,
                _registered_method=True)
        self.GetTelemetrylineNodes = channel.unary_unary(
                '/clone.valve_driver.ValveDriverGRPC/GetTelemetrylineNodes',
                request_serializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.GetNodesMessage.SerializeToString,
                response_deserializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.NodeList.FromString,
                _registered_method=True)


class ValveDriverGRPCServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SendDirect(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendManyDirect(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendImpulse(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendManyImpulse(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendPulse(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendPinchValveControl(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendManyPinchValveControl(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StreamManyPinchValveControl(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendPinchValveCommand(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendManyPinchValveCommand(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendManyPressure(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StreamManyPressure(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAllNodes(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetControllineNodes(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetTelemetrylineNodes(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ValveDriverGRPCServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SendDirect': grpc.unary_unary_rpc_method_handler(
                    servicer.SendDirect,
                    request_deserializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendDirectMessage.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'SendManyDirect': grpc.unary_unary_rpc_method_handler(
                    servicer.SendManyDirect,
                    request_deserializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyDirectMessage.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'SendImpulse': grpc.unary_unary_rpc_method_handler(
                    servicer.SendImpulse,
                    request_deserializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendImpulseMessage.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'SendManyImpulse': grpc.unary_unary_rpc_method_handler(
                    servicer.SendManyImpulse,
                    request_deserializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyImpulseMessage.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'SendPulse': grpc.unary_unary_rpc_method_handler(
                    servicer.SendPulse,
                    request_deserializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendPulseMessage.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'SendPinchValveControl': grpc.unary_unary_rpc_method_handler(
                    servicer.SendPinchValveControl,
                    request_deserializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendPinchValveControlMessage.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'SendManyPinchValveControl': grpc.unary_unary_rpc_method_handler(
                    servicer.SendManyPinchValveControl,
                    request_deserializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyPinchValveControlMessage.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'StreamManyPinchValveControl': grpc.stream_unary_rpc_method_handler(
                    servicer.StreamManyPinchValveControl,
                    request_deserializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyPinchValveControlMessage.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'SendPinchValveCommand': grpc.unary_unary_rpc_method_handler(
                    servicer.SendPinchValveCommand,
                    request_deserializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendPinchValveCommandMessage.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'SendManyPinchValveCommand': grpc.unary_unary_rpc_method_handler(
                    servicer.SendManyPinchValveCommand,
                    request_deserializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyPinchValveCommandMessage.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'SendManyPressure': grpc.unary_unary_rpc_method_handler(
                    servicer.SendManyPressure,
                    request_deserializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyPressureMessage.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'StreamManyPressure': grpc.stream_unary_rpc_method_handler(
                    servicer.StreamManyPressure,
                    request_deserializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyPressureMessage.FromString,
                    response_serializer=clone__client_dot_proto_dot_data__types__pb2.ServerResponse.SerializeToString,
            ),
            'GetAllNodes': grpc.unary_unary_rpc_method_handler(
                    servicer.GetAllNodes,
                    request_deserializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.GetNodesMessage.FromString,
                    response_serializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.NodeList.SerializeToString,
            ),
            'GetControllineNodes': grpc.unary_unary_rpc_method_handler(
                    servicer.GetControllineNodes,
                    request_deserializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.GetNodesMessage.FromString,
                    response_serializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.NodeList.SerializeToString,
            ),
            'GetTelemetrylineNodes': grpc.unary_unary_rpc_method_handler(
                    servicer.GetTelemetrylineNodes,
                    request_deserializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.GetNodesMessage.FromString,
                    response_serializer=clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.NodeList.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'clone.valve_driver.ValveDriverGRPC', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('clone.valve_driver.ValveDriverGRPC', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ValveDriverGRPC(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SendDirect(request,
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
            '/clone.valve_driver.ValveDriverGRPC/SendDirect',
            clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendDirectMessage.SerializeToString,
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
    def SendManyDirect(request,
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
            '/clone.valve_driver.ValveDriverGRPC/SendManyDirect',
            clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyDirectMessage.SerializeToString,
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
    def SendImpulse(request,
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
            '/clone.valve_driver.ValveDriverGRPC/SendImpulse',
            clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendImpulseMessage.SerializeToString,
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
    def SendManyImpulse(request,
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
            '/clone.valve_driver.ValveDriverGRPC/SendManyImpulse',
            clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyImpulseMessage.SerializeToString,
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
    def SendPulse(request,
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
            '/clone.valve_driver.ValveDriverGRPC/SendPulse',
            clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendPulseMessage.SerializeToString,
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
    def SendPinchValveControl(request,
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
            '/clone.valve_driver.ValveDriverGRPC/SendPinchValveControl',
            clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendPinchValveControlMessage.SerializeToString,
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
    def SendManyPinchValveControl(request,
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
            '/clone.valve_driver.ValveDriverGRPC/SendManyPinchValveControl',
            clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyPinchValveControlMessage.SerializeToString,
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
    def StreamManyPinchValveControl(request_iterator,
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
            '/clone.valve_driver.ValveDriverGRPC/StreamManyPinchValveControl',
            clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyPinchValveControlMessage.SerializeToString,
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
    def SendPinchValveCommand(request,
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
            '/clone.valve_driver.ValveDriverGRPC/SendPinchValveCommand',
            clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendPinchValveCommandMessage.SerializeToString,
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
    def SendManyPinchValveCommand(request,
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
            '/clone.valve_driver.ValveDriverGRPC/SendManyPinchValveCommand',
            clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyPinchValveCommandMessage.SerializeToString,
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
    def SendManyPressure(request,
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
            '/clone.valve_driver.ValveDriverGRPC/SendManyPressure',
            clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyPressureMessage.SerializeToString,
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
    def StreamManyPressure(request_iterator,
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
            '/clone.valve_driver.ValveDriverGRPC/StreamManyPressure',
            clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.SendManyPressureMessage.SerializeToString,
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
    def GetAllNodes(request,
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
            '/clone.valve_driver.ValveDriverGRPC/GetAllNodes',
            clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.GetNodesMessage.SerializeToString,
            clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.NodeList.FromString,
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
    def GetControllineNodes(request,
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
            '/clone.valve_driver.ValveDriverGRPC/GetControllineNodes',
            clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.GetNodesMessage.SerializeToString,
            clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.NodeList.FromString,
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
    def GetTelemetrylineNodes(request,
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
            '/clone.valve_driver.ValveDriverGRPC/GetTelemetrylineNodes',
            clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.GetNodesMessage.SerializeToString,
            clone__client_dot_valve__driver_dot_proto_dot_valve__driver__pb2.NodeList.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
