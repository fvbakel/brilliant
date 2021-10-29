cmake_minimum_required(VERSION 3.10.0)
project(hello_cppflow VERSION 0.1.0)

find_library(TENSORFLOW_LIB tensorflow HINT $ENV{HOME}/libtensorflow2/lib)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-omit-frame-pointer -fsanitize=address")
set(CMAKE_LINKER_FLAGS "${CMAKE_LINKER_FLAGS} -lasan")
find_package( OpenCV REQUIRED )
# find_package( OpenCV REQUIRED PATHS /usr/local NO_DEFAULT_PATH)

add_executable(hello_cppflow main.cpp)
target_include_directories(hello_cppflow PRIVATE /home/fvbakel/git/cppflow/include $ENV{HOME}/libtensorflow2/include)
target_link_libraries (hello_cppflow "${TENSORFLOW_LIB}" ${OpenCV_LIBS} stdc++fs)
