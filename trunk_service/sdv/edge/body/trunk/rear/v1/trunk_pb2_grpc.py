# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from sdv.edge.body.trunk.rear.v1 import trunk_pb2 as sdv_dot_edge_dot_body_dot_trunk_dot_rear_dot_v1_dot_trunk__pb2


class RearTrunkStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SetOpenStatus = channel.unary_unary(
                '/sdv.edge.body.trunk.rear.v1.RearTrunk/SetOpenStatus',
                request_serializer=sdv_dot_edge_dot_body_dot_trunk_dot_rear_dot_v1_dot_trunk__pb2.OpenRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )


class RearTrunkServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SetOpenStatus(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RearTrunkServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SetOpenStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.SetOpenStatus,
                    request_deserializer=sdv_dot_edge_dot_body_dot_trunk_dot_rear_dot_v1_dot_trunk__pb2.OpenRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'sdv.edge.body.trunk.rear.v1.RearTrunk', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class RearTrunk(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SetOpenStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/sdv.edge.body.trunk.rear.v1.RearTrunk/SetOpenStatus',
            sdv_dot_edge_dot_body_dot_trunk_dot_rear_dot_v1_dot_trunk__pb2.OpenRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
