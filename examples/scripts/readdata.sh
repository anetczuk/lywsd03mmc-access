#!/bin/bash

set -eu
set -o pipefail     ## makes the pipeline return the exit status of the first failed command (handy for ts command)


SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


# shellcheck disable=SC1091
source "${SCRIPT_DIR}/_tools.sh"
find_read_config


SRC_DIR="${SCRIPT_DIR}"/../../src


SLEEP_VALUE=-1
OUT_MEASURE_FILE="/tmp/read_measurements.txt"

while [[ $# -gt 0 ]]; do
    case $1 in
      --sleep=*)    SLEEP_VALUE="${1#*=}"
                    shift # past argument
                    ;;
      --outfile=*)  OUT_MEASURE_FILE="${1#*=}"
                    shift # past argument
                    ;;
      -*)       echo "Unknown option $1"
                exit 1
                ;;
      *)    shift # past argument
            ;;
    esac
done


if [[ ${SLEEP_VALUE} -lt 0 ]]; then
    ## single read mode
    python3 "${SRC_DIR}"/lywsd03mmcaccess/main.py -la readdata --mac "${MAC_ADDRESS}" "$@"
    exit 0
fi


##
## run in loop mode
##

true > "${OUT_MEASURE_FILE}"     ## clear file

echo "writing measurements to file: ${OUT_MEASURE_FILE}"
while true; do
    if ! python3 "${SRC_DIR}"/lywsd03mmcaccess/main.py -nl readdata --mac "${MAC_ADDRESS}" "$@" 2> /dev/null | \
         ts '[%H:%M:%.S]' | \
         tee -a "${OUT_MEASURE_FILE}"
    then
        echo "could not get data from device"
        sleep 1
    else
        sleep "${SLEEP_VALUE}"
    fi
done
