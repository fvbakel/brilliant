#!/bin/sh
CC_RELEASE="g++ -Ofast" 
CC_DEBUG="g++ -g"
x=nonogram

clear
echo "Compile start"
#$CC_DEBUG -I /usr/include/opencv4/ ./hello_world_opencv.cpp -o debug_hello_world_opencv

if [ -n "$1" ]; then
  echo "Skipping release compile"
  if [ "$1" = "test" ]; then
    ./test_nonogram
  fi
else
    echo "Compiling released"
    # $CC_RELEASE -I ./headers/ ./classes/*.cpp ./main.cpp -o nonogram
    
     $CC_RELEASE -I /usr/include/opencv4/ ./hello_world_opencv.cpp -L /usr/lib/x86_64-linux-gnu/libopencv_core.so /usr/lib/x86_64-linux-gnu/libopencv_highgui.so -o hello_world_opencv
fi

echo "Compile ready"
