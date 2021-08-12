#!/bin/sh
CC="gcc -Ofast -march=native -mtune=native -funroll-all-loops" 
x=clowns
$CC -o $x $x.c -lm

