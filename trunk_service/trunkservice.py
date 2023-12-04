import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import os
import signal
import threading
from threading import Thread
import time
from typing import Any, Dict, Optional, Tuple
from google.protobuf.empty_pb2 import Empty

import grpc
from sdv.databroker.v1.collector_pb2_grpc import CollectorStub
from sdv.databroker.v1.collector_pb2 import (
  RegisterDatapointsRequest,
  RegistrationMetadata,
  UpdateDatapointsRequest
)
from sdv.databroker.v1.types_pb2 import ChangeType, DataType
from sdv.edge.body.trunk.rear.v1.trunk_pb2 import (
  OpenRequest
)
from sdv.edge.body.trunk.rear.v1.trunk_pb2_grpc import (
  RearTrunkServicer,
  add_RearTrunkServicer_to_server
)

log = logging.getLogger("trunk_service")
event = threading.Event()

SERVICE_ADDRESS = os.getenv("SERVICE_ADDRESS", "0.0.0.0:50053")
VDB_ADDRESS = os.getenv("VDB_ADDRESS", "127.0.0.1:55555")

def is_grpc_fatal_error(e: grpc.RpcError) -> bool:
  if (
    e.code() == grpc.StatusCode.UNAVAILABLE
    or e.code() == grpc.StatusCode.UNKNOWN
    or e.code() == grpc.StatusCode.UNAUTHENTICATED
    or e.code() == grpc.StatusCode.INTERNAL
  ):
    log.error("Feeding aborted due to RpcError(%s, '%s')", e.code(), e.details())
    return True
  else:
    log.warning("Unhandled RpcError(%s, '%s')", e.code(), e.details())
    return False

class TrunkService:
  def __init__(self, address):
    if os.getenv("DAPR_GRPC_PORT") is not None:
      grpc_port = os.getenv("DAPR_GRPC_PORT")
      self._vdb_address = f"127.0.0.1:{grpc_port}"
    else:
      self._vdb_address = VDB_ADDRESS

    self._address = address
    self._metadata: Optional[Tuple[Tuple[str, Optional[str]]]] = None
    self._connected = False
    self._registered = False
    self._shutdown = False
    self._ids: Dict[str, Any] = {}
    self._databroker_thread = Thread(
      target=self.connect_to_databroker, daemon=True, name="databroker-connector"
    )
    self._databroker_thread.start()

  def connect_to_databroker(self) -> None:
    log.info("Connecting to databroker [%s]", self._vdb_address)
    if os.getenv("VEHICLEDATABROKER_DAPR_APP_ID") is not None:
      self._metadata = (
        ("dapr-app-id", os.getenv("VEHICLEDATABROKER_DAPR_APP_ID")),
      )
      time.sleep(1)
    else:
      self._metadata = None
    self._channel: grpc.Channel = grpc.insecure_channel(self._vdb_address)
    self._stub = CollectorStub(self._channel)
    log.info("Using gRPC metadata: %s", self._metadata)
    self._channel.subscribe(
      lambda connectivity: self.on_broker_connectivity_change(connectivity),
      try_to_connect=False
    )
    self._run()

  def on_broker_connectivity_change(self, connectivity: grpc.ChannelConnectivity) -> None:
    log.info("Databroker connectivity changed to %s", connectivity)
    if (
      connectivity == grpc.ChannelConnectivity.READY
      or connectivity == grpc.ChannelConnectivity.IDLE
    ):
      # Only act on unnconencted state
      if not self._connected:
        log.info("Connected to data broker")
        try:
          self.register_datapoints()
          log.info("datapoints are registered.")
          self._registered = True
        except grpc.RpcError as err:
          log.error("Failed to register datapoints")
          is_grpc_fatal_error(err)
        except Exception:
          log.error("Failed to register datapoints", exc_info=True)
        self._connected = True
      else:
        if self._connected:
          log.info("Disconnected from data broker")
        else:
          if connectivity == grpc.ChannelConnectivity.CONNECTING:
            log.info("Trying to connect to data broker")
      self._connected = False
      self._registered = False

  def _run(self) -> None:
    while self._shutdown is False:
      if not self._connected:
        time.sleep(0.2)
        continue
      elif not self._registered:
        try:
          log.debug("Trying to register datapoints")
          self._register_datapoints()
          self._registered = True
        except grpc.RpcError as err:
          is_grpc_fatal_error(err)
          log.debug("Failed to register datapoints", exc_info=True)
          time.sleep(3)
        except Exception:
          log.error("Failed to register datapoints", exc_info=True)
          time.sleep(1)
          continue
      else:
        time.sleep(1)

  def serve(self) -> None:
    log.info("Starting trunk service on %s", self._address)
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    _servicer = self._TrunkService(self)
    add_RearTrunkServicer_to_server(_servicer, server)
    server.add_insecure_port(self._address)
    server.start()
    server.wait_for_termination()

  async def close(self) -> None:
    if self._channel:
      await self._channel.close()

  def __enter__(self) -> "TrunkService":
    return self
  
  def __exit__(self, exc_type, exc_value, traceback) -> None:
    asyncio.run_coroutine_threadsafe(self.close(), asyncio.get_event_loop())

  def register_datapoints(self):
    log.info("Try register datapoints")
    self.register(
      "Vehicle.Body.Trunk.Rear.IsOpen",
      DataType.BOOL,
      ChangeType.ON_CHANGE
    )
  
  def register(self, name, data_type, change_type) -> None:
    self._register(name, data_type, change_type)

  def _register(self, name, data_type, change_type) -> None:
    request = RegisterDatapointsRequest()
    registration_metadata = RegistrationMetadata()
    registration_metadata.name = name
    registration_metadata.data_type = data_type
    registration_metadata.change_type = change_type
    registration_metadata.description = "Rear trunk status"
    request.list.append(registration_metadata)
    response = self._stub.RegisterDatapoints(request, metadata=self._metadata)
    self._ids[name] = response.results[name]

  def set_bool_datapoint(self, name: str, value: bool):
    _id = self._ids[name]
    request = UpdateDatapointsRequest()
    request.datapoints[_id].bool_value = value
    log.info("Feeding '%s' with value %s", name, value)
    try:
      self._stub.UpdateDatapoints(request, metadata=self._metadata)
    except grpc.RpcError as err:
      log.warning("Failed to feed '%s' with value %s", name, value)
      self._connected = is_grpc_fatal_error(err)
      raise err
    
  class _TrunkService(RearTrunkServicer):
    def __init__(self, servicer):
      self._servicer: TrunkService = servicer

    def SetOpenStatus(self, request: OpenRequest, context):
      log.info("* Request to set open status to %s", str(request).replace("\n", " "))
      self._servicer.set_bool_datapoint("Vehicle.Body.Trunk.Rear.IsOpen", request.is_open)
      log.info(" Trunk status updated\n")
      return Empty()

async def main():
  trunk_service = TrunkService(SERVICE_ADDRESS)
  trunk_service.serve()

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  log.setLevel(logging.DEBUG)
  LOOP = asyncio.get_event_loop()
  LOOP.add_signal_handler(signal.SIGINT, LOOP.stop)
  LOOP.run_until_complete(main())
  LOOP.close()