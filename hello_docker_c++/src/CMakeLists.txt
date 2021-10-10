cmake_minimum_required(VERSION 3.10)

# set the project name
project(Helloworld)

# specify the C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

#/usr/share/OpenCV/OpenCVConfig.cmake
set (OpenCV_DIR /usr/share/OpenCV)
find_package(OpenCV REQUIRED core )

# add the executable
add_executable(Helloworld main.cpp)

#include_directories( ${OpenCV_INCLUDE_DIRS} )
#target_link_libraries( HelloworldLib ${OpenCV_LIBS} 

target_include_directories(Helloworld PUBLIC
                           "${PROJECT_BINARY_DIR}"
                           "${OpenCV_LIBS}"
                           )

# add the install targets
install(TARGETS Helloworld DESTINATION bin)
#install(FILES "${PROJECT_BINARY_DIR}/TutorialConfig.h"
#  DESTINATION include
#  )

