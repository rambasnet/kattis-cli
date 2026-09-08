#!/usr/bin/env bash

count_negative() {
    local count=0
    local temperature

    for temperature in "$@"; do
        if (( temperature < 0 )); then
            count=$((count + 1))
        fi
    done

    echo "$count"
}

main() {
    local n
    local -a temperatures

    read -r n
    read -r -a temperatures

    count_negative "${temperatures[@]}"
}

# Run main only when executed directly, not when sourced by tests.
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    main
fi