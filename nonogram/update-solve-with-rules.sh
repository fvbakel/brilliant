#!/bin/sh
./compile.sh
./test_nonogram | grep improve > ./to_solve_with_rules.txt
