#!/bin/bash

set -eu


SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


# shellcheck disable=SC1091
source "${SCRIPT_DIR}/_tools.sh"
find_read_config


SRC_DIR="${SCRIPT_DIR}"/../../src


python3 "${SRC_DIR}"/lywsd03mmcaccess/main.py info --mac "${MAC_ADDRESS}" "$@"
