#!/usr/bin/env python3
# /********************************************************************************
# * Copyright (c) 2022 Contributors to the Eclipse Foundation
# *
# * See the NOTICE file(s) distributed with this work for additional
# * information regarding copyright ownership.
# *
# * This program and the accompanying materials are made available under the
# * terms of the Apache License 2.0 which is available at
# * http://www.apache.org/licenses/LICENSE-2.0
# *
# * SPDX-License-Identifier: Apache-2.0
# ********************************************************************************/

import getopt
import logging
import os
import sys

import grpc
import sdv.edge.body.trunk.rear.v1.trunk_pb2 as pb2
import sdv.edge.body.trunk.rear.v1.trunk_pb2_grpc as pb2_grpc

logger = logging.getLogger(__name__)


class TrunkTestClient(object):
    """
    Client for gRPC functionality
    """

    def __init__(self, trunk_addr: str):
        self._trunk_addr = trunk_addr
        logger.info("Connecting to TRUNK service %s", self._trunk_addr)

        # instantiate a channel
        self.channel = grpc.insecure_channel(self._trunk_addr)

        # bind the client and the server
        self.stub = pb2_grpc.RearTrunkStub(self.channel)

    def set_trunk_status(self, trunk_status: bool) -> None:
        """
        Client function to call the rpc for HVACService methods
        """
        logger.info("Setting Trunk Status: %s", trunk_status)
        request = pb2.OpenRequest(is_open=trunk_status)
        self.stub.SetOpenStatus(request)

        logger.debug("Done.")


def main(argv):
    """Main function"""

    default_addr = "127.0.0.1:50053"
    default_status = False

    _usage = (
        "Usage: ./testclient.py --addr <host:name>"  # shorten line
        " --status=TRUNK_STATUS\n\n"
        "Environment:\n"
        "  'VDB_ADDR'     Databroker address (host:port). Default: {}\n"
        "  'TRUNK_STATUS' Desired trunk status. Default: {}\n".format(
            default_addr, default_status
        )
    )

    # environment values (overridden by cmdargs)
    trunk_addr = os.getenv("TRUNK_ADDR", default_addr)
    trunk_status = False

    # parse cmdline args
    try:
        opts, args = getopt.getopt(argv, "ha:s:", ["addr=", "status="])
        for opt, arg in opts:
            if opt == "-h":
                print(_usage)
                sys.exit(0)
            elif opt in ("-a", "--addr"):
                trunk_addr = arg
            elif opt in ("-s", "--status"):
                trunk_status = True if arg != "0" else False
            else:
                print("Unknown arg: {}".format(opt))
                print(_usage)
                sys.exit(1)
    except getopt.GetoptError:
        print(_usage)
        sys.exit(1)

    client = TrunkTestClient(trunk_addr)
    client.set_trunk_status(trunk_status)


if __name__ == "__main__":
    logging.basicConfig(level=os.getenv("CLI_LOG_LEVEL", "INFO"))
    main(sys.argv[1:])