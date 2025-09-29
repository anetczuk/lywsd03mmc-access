#!/bin/bash

set -eu


# works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

SRC_DIR="${SCRIPT_DIR}"/../src


##
## generate history chart
##

HIST_DATA_PATH="${SCRIPT_DIR}"/example_history.json
HIST_CHART_PATH="${SCRIPT_DIR}"/example_history.png
"${SRC_DIR}"/lywsd03mmcaccess/main.py printhistory --infile "${HIST_DATA_PATH}" --outchart "${HIST_CHART_PATH}" --noprint


##
## generate measurements chart
##

RAW_DATA_FILE="${SCRIPT_DIR}/unfreeze_measurements.txt"
JSON_DATA_FILE="${SCRIPT_DIR}/unfreeze_measurements.json"
python3 "${SRC_DIR}"/lywsd03mmcaccess/main.py -la convertmeasurements --infile "${RAW_DATA_FILE}" --outfile "${JSON_DATA_FILE}" --noprint

MEASURE_CHART_PATH="${SCRIPT_DIR}"/unfreeze_measurements.png
"${SRC_DIR}"/lywsd03mmcaccess/main.py printhistory --infile "${JSON_DATA_FILE}" --outchart "${MEASURE_CHART_PATH}" --noprint


echo -e "\nall generated"
