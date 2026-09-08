#!/usr/bin/env bats
# to run: `bats tests/test_cold.bats` from bash folder 
setup() {
    source "$BATS_TEST_DIRNAME/../src/cold.sh"
}

@test "debug test directory" {
    printf 'Test directory: <%s>\n' "$BATS_TEST_DIRNAME"
    printf 'Working directory: <%s>\n' "$PWD"
    true
}

@test "counts negative temperatures in mixed input" {
    run count_negative -10 5 -3 0 8
    [ "$status" -eq 0 ]
    [ "$output" = "2" ]
}

@test "counts all temperatures when all are negative" {
    run count_negative -1 -20 -5
    [ "$status" -eq 0 ]
    [ "$output" = "3" ]
}

@test "does not count zero or positive temperatures" {
    run count_negative 0 1 20 0
    [ "$status" -eq 0 ]
    [ "$output" = "0" ]
}

@test "handles a single negative temperature" {
    run count_negative -7
    [ "$status" -eq 0 ]
    [ "$output" = "1" ]
}

@test "complete script reads input and prints the answer" {
    run bash "$BATS_TEST_DIRNAME/src/cold.sh" <<'EOF'
5
-10 5 -3 0 8
EOF
    [ "$status" -eq 0 ]
    [ "$output" = "2" ]
}