#!/bin/bash

set -eu


# works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

SRC_DIR="${SCRIPT_DIR}"/../src


##
## generate history chart
##

echo "generate example history chart"
HIST_DATA_PATH="${SCRIPT_DIR}"/example_history.json
HIST_CHART_PATH="${SCRIPT_DIR}"/example_history.png
"${SRC_DIR}"/lywsd03mmcaccess/main.py printhistory --infile "${HIST_DATA_PATH}" --outchart "${HIST_CHART_PATH}" --noprint


##
## generate measurements chart
##

echo "generate fridge in chart"
RAW_DATA_FILE="${SCRIPT_DIR}/fridge_in_measurements.txt"
JSON_DATA_FILE="${SCRIPT_DIR}/fridge_in_measurements.json"
python3 "${SRC_DIR}"/lywsd03mmcaccess/main.py -la convertmeasurements --infile "${RAW_DATA_FILE}" --outfile "${JSON_DATA_FILE}" --noprint

MEASURE_CHART_PATH="${SCRIPT_DIR}"/fridge_in_measurements.png
"${SRC_DIR}"/lywsd03mmcaccess/main.py printhistory --infile "${JSON_DATA_FILE}" --outchart "${MEASURE_CHART_PATH}" --noprint


echo "generate fridge out chart"
RAW_DATA_FILE="${SCRIPT_DIR}/fridge_out_measurements.txt"
JSON_DATA_FILE="${SCRIPT_DIR}/fridge_out_measurements.json"
python3 "${SRC_DIR}"/lywsd03mmcaccess/main.py -la convertmeasurements --infile "${RAW_DATA_FILE}" --outfile "${JSON_DATA_FILE}" --noprint

MEASURE_CHART_PATH="${SCRIPT_DIR}"/fridge_out_measurements.png
"${SRC_DIR}"/lywsd03mmcaccess/main.py printhistory --infile "${JSON_DATA_FILE}" --outchart "${MEASURE_CHART_PATH}" --noprint


echo "generate fridge stability chart"
JSON_DATA_FILE="${SCRIPT_DIR}/fridge_stability.json"
MEASURE_CHART_PATH="${SCRIPT_DIR}"/fridge_stability.png
"${SRC_DIR}"/lywsd03mmcaccess/main.py printhistory --infile "${JSON_DATA_FILE}" --outchart "${MEASURE_CHART_PATH}" --noprint
"${SRC_DIR}"/lywsd03mmcaccess/main.py printhistory --infile "${JSON_DATA_FILE}" --outchart "${MEASURE_CHART_PATH}" --noprint


echo "generate room stability chart"
JSON_DATA_FILE="${SCRIPT_DIR}/room_stability.json"
MEASURE_CHART_PATH="${SCRIPT_DIR}"/room_stability.png
"${SRC_DIR}"/lywsd03mmcaccess/main.py printhistory --infile "${JSON_DATA_FILE}" --outchart "${MEASURE_CHART_PATH}" --noprint


echo "generate outdoor stability chart"
JSON_DATA_FILE="${SCRIPT_DIR}/outdoor_stability.json"
MEASURE_CHART_PATH="${SCRIPT_DIR}"/outdoor_stability.png
"${SRC_DIR}"/lywsd03mmcaccess/main.py printhistory --infile "${JSON_DATA_FILE}" --outchart "${MEASURE_CHART_PATH}" --noprint


echo -e "\nall generated"
