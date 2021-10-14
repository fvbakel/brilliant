cmake_minimum_required(VERSION 3.0.0)
project(hello_tesseract VERSION 0.1.0)

include(CTest)
enable_testing()

#find_package( Tesseract REQUIRED )
find_package( PkgConfig REQUIRED)

pkg_search_module( TESSERACT REQUIRED tesseract )
pkg_search_module( LEPTONICA REQUIRED lept )

add_executable(hello_tesseract main.cpp)

target_link_libraries( hello_tesseract ${TESSERACT_LIBRARIES} )
target_link_libraries( hello_tesseract ${LEPTONICA_LIBRARIES} )

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)

add_test(NAME run COMMAND hello_tesseract)