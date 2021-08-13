#!/bin/sh
CC="gcc -Ofast -march=native -mtune=native -funroll-all-loops" 
x=sudoku
$CC -o $x $x.c -lm

