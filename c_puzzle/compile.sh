#!/bin/sh
CC="gcc -Ofast -march=native -mtune=native -funroll-all-loops" 

compile() 
{
    echo compiling $1
    $CC -o $1 $1.c -lm
}

if [ -z "$1" ]
  then
    compile clowns
    compile prison-problem
    compile size-of-types
    compile prison-problem-alt-1
    compile bit-array
else
    compile $1
fi





