#!/bin/sh
#CC="g++ -Ofast -march=native -mtune=native -funroll-all-loops" 
CC="g++"
x=nonogram

clear
echo "compile start"
$CC -I ./headers/ *.cpp ./test/test_nonogram.cpp -o test_nonogram #-lm
#$CC -I ./ -c Piece.cpp  #-lm
#$CC -I ./headers/ -c nonogram.cpp Piece.cpp #-o $x #-lm
#$CC -o $x nonogram.o Piece.o
echo "compile ready"
