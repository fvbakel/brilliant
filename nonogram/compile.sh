#!/bin/sh
CC_RELEASE="g++ -Ofast -march=native -mtune=native -funroll-all-loops" 
CC_DEBUG="g++ -g"
x=nonogram

clear
echo "compile start"
$CC_DEBUG -I ./headers/ ./classes/*.cpp ./test/test_nonogram.cpp -o test_nonogram

$CC_RELEASE -I ./headers/ ./classes/*.cpp ./main.cpp -o nonogram

echo "compile ready"
