#!/bin/bash

set -eu


# works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

SRC_DIR="${SCRIPT_DIR}"/../src



HIST_DATA_PATH="${SCRIPT_DIR}"/example_history.json
HIST_CHART_PATH="${SCRIPT_DIR}"/example_history.png
"${SRC_DIR}"/lywsd03mmcaccess/main.py printhistory --histfile "${HIST_DATA_PATH}" --outchart "${HIST_CHART_PATH}" --noprint


echo -e "\nall generated"
