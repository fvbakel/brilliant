cmake_minimum_required(VERSION 3.8.0 FATAL_ERROR)

set(CMAKE_AUTOMOC ON)

find_package(Qt5 COMPONENTS Widgets REQUIRED)

add_executable(imageviewer main.cpp imageviewer.cpp imageviewer.h)
target_link_libraries(imageviewer Qt5::Widgets)