#!/bin/bash

set -eu


SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


MAC_ADDRESS=""
ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
      --mac=*)    MAC_ADDRESS="${1#*=}"
                  shift  ## pop argument
                  ;;
      --mac)      MAC_ADDRESS="${2}"
                  shift 2  ## pop 2 arguments
                  ;;
      *)    ARGS+=("${1}")
            shift # pop argument
            ;;
    esac
done


if [[ -z "${MAC_ADDRESS}" ]]; then
    ## MAC address not given - load it from config

    # shellcheck disable=SC1091
    source "${SCRIPT_DIR}/_tools.sh"
    find_read_config
fi


SRC_DIR="${SCRIPT_DIR}"/../../src


python3 "${SRC_DIR}"/lywsd03mmcaccess/main.py -la readhistory --mac "${MAC_ADDRESS}" "${ARGS[@]}"
