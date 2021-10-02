#!/bin/sh
CC_RELEASE="g++ -Ofast -march=native -mtune=native -funroll-all-loops" 
CC_DEBUG="g++ -g"
x=nonogram

clear
echo "Compile start"
$CC_DEBUG -I ./headers/ ./classes/*.cpp ./test/test_nonogram.cpp -o test_nonogram

if [ -n "$1" ]; then
  echo "Skipping release compile"
else
    echo "Compiling released"
    $CC_RELEASE -I ./headers/ ./classes/*.cpp ./main.cpp -o nonogram
fi

echo "Compile ready"
