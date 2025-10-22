#!/bin/bash


## $1 - start directory
## $2 - subpath to search
find_parent() {
    local current_dir="${1}"
    local search_path="${2}"

    while [ "$current_dir" != "/" ]; do
        if [ -f "$current_dir/${search_path}" ]; then
            echo "$current_dir"
            return
        fi
        current_dir=$(dirname "$current_dir")
    done

    ## check root directory
    if [ -f "$current_dir/${search_path}" ]; then
        echo "$current_dir"
        return
    fi
    
    ## not found
    echo ""
}


## $1 - start directory
## $2 - subpath to search
find_file() {
    local found_path=$(find_parent "${1}" "${2}")
    if [[ "${found_path}" != "" ]]; then
        echo "${found_path}/${2}"
    else
        echo ""
    fi
}


find_read_config() {
    found_config=$(find_file "${SCRIPT_DIR}" "config.bash")
    if [[ "${found_config}" == "" ]]; then
        echo "unable to find config file"
        exit 1
    fi
    
    echo "found config: ${found_config}"
    
    # shellcheck disable=SC1090
    source "${found_config}"
}
