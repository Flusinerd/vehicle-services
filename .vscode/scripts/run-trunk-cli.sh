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
echo "### Running TRUNK Client                             ###"
echo "#######################################################"

set -e

ROOT_DIRECTORY=$(git rev-parse --show-toplevel)
# shellcheck source=/dev/null
source "$ROOT_DIRECTORY/.vscode/scripts/task-common.sh" "$@"

STATUS="$1"

# sanity checks for invalid user input
if [ -z "$STATUS" ]; then
	echo "Invalid arguments!"
	echo
	echo "Usage: $0 TRUNK_STATUS [OPEN|CLOSED]"
	echo
	exit 1
fi

# replace [OPEN/CLOSED] with [1/0] for AC_STATUS
if [ "$STATUS_MODE" = "OPEN" ]; then
	STATUS="1"
else
	STATUS="0"
fi

# gRPC port of trunk service (no dapr!)
TRUNKSERVICE_PORT='50053'
TRUNKSERVICE_EXEC_PATH="$ROOT_DIRECTORY/trunk_service"
if [ ! -f "$TRUNKSERVICE_EXEC_PATH/testclient.py" ]; then
	echo "Can't find $TRUNKSERVICE_EXEC_PATH/testclient.py"
	exit 1
fi

cd "$TRUNKSERVICE_EXEC_PATH" || exit 1
pip3 install -q -r requirements.txt

## Uncomment to reduce logs from client
# export CLI_LOG_LEVEL="WARNING"

# set -x
python3 -u testclient.py --addr=localhost:$TRUNKSERVICE_PORT --status=$STATUS
