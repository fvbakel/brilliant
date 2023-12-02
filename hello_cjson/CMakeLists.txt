cmake_minimum_required(VERSION 3.10)

# set the project name and version
project(hello_cjson VERSION 1.0)

# specify the C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

find_package(cJSON REQUIRED)

# add the executable
add_executable(hello_cjson hello_cjson.c)

target_link_libraries( hello_cjson ${CJSON_LIBRARIES} )

cmake_minimum_required(VERSION 3.10)


target_include_directories(hello_cjson PUBLIC
                           "${PROJECT_BINARY_DIR}"
                           )
