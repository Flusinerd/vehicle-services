#!/bin/bash
#********************************************************************************
# Copyright (c) 2022 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License 2.0 which is available at
# http://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
#*******************************************************************************/
# shellcheck disable=SC2034
# shellcheck disable=SC2086

echo "#######################################################"
echo "### Running TRUNK Service                           ###"
echo "#######################################################"

set -e

ROOT_DIRECTORY=$(git rev-parse --show-toplevel)
# shellcheck source=/dev/null
source "$ROOT_DIRECTORY/.vscode/scripts/task-common.sh" "$@"

### NOTE: TRUNKSERVICE* variables are defined in task-common.sh
# TRUNKSERVICE_PORT='50053'
# TRUNKSERVICE_GRPC_PORT='52005'
# TRUNKSERVICEDAPR_APP_ID='trunkservi_ce'
# VEHICLEDATABROKER_DAPR_APP_ID='vehicledatabroker'

# NOTE: use curent sidecar's grpc port, don't connect directly to sidecar of kdb (DATABROKER_GRPC_PORT)
export DAPR_GRPC_PORT=$TRUNKSERVICE_GRPC_PORT

TRUNKSERVICEEXEC_PATH="$ROOT_DIRECTORY/trunk_service"
if [ ! -f "$TRUNKSERVICEEXEC_PATH/trunkservice.py" ]; then
	echo "Can't find $TRUNKSERVICEEXEC_PATH/trunkservice.py"
	exit 1
fi

cd "$TRUNKSERVICEEXEC_PATH" || exit 1
pip3 install -q -r requirements.txt

echo
echo "*******************************************"
echo "* Hvac Service app-id: $TRUNKSERVICE_DAPR_APP_ID"
echo "* Hvac Service APP port: $TRUNKSERVICE_PORT"
echo "* Hvac Service Dapr sidecar port: $TRUNKSERVICE_GRPC_PORT"
echo "* DAPR_GRPC_PORT=$DAPR_GRPC_PORT"
echo "* metadata: [ VEHICLEDATABROKER_DAPR_APP_ID=$VEHICLEDATABROKER_DAPR_APP_ID ]"
echo "*******************************************"
echo

## uncomment for dapr debug logs
# DAPR_OPT="--enable-api-logging --log-level debug"1
DAPR_OPT="--log-level warn"
dapr run \
	--app-id $TRUNKSERVICE_DAPR_APP_ID \
	--app-protocol grpc \
	--app-port $TRUNKSERVICE_PORT \
	--dapr-grpc-port $TRUNKSERVICE_GRPC_PORT \
	$DAPR_OPT \
	--components-path $ROOT_DIRECTORY/.dapr/components \
	--config $ROOT_DIRECTORY/.dapr/config.yaml \
	-- \
	python3 -u ./trunkservice.py
