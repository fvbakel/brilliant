cmake_minimum_required(VERSION 3.8.0 FATAL_ERROR)

project(Qt4And5)

set(CMAKE_AUTOMOC ON)

find_package(Qt5 COMPONENTS Widgets REQUIRED)

add_subdirectory(hello_qt_creator)
add_subdirectory(imageviewer)

add_executable(Hello_QT main.cpp)
target_link_libraries(Hello_QT Qt5::Widgets)
