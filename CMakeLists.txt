cmake_minimum_required(VERSION 3.17)

project(
  pymatcalc
  LANGUAGES CXX
  VERSION 1.0)

set(CMAKE_CXX_STANDARD 17)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/include")
set(PYMATCALC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/pymatcalc")

include_directories("${INCLUDE_DIR}")

add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/vendor/dylib" EXCLUDE_FROM_ALL)

find_package(SWIG REQUIRED)
find_package(Python3 COMPONENTS Interpreter Development)

include(UseSWIG)

# pymatcalc
execute_process(
  COMMAND "${Python3_EXECUTABLE}" -c
          "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))"
  OUTPUT_VARIABLE EXT_SUFFIX
  OUTPUT_STRIP_TRAILING_WHITESPACE)

set_property(SOURCE "pymatcalc.i" PROPERTY CPLUSPLUS ON)
swig_add_library(
  pymatcalc
  LANGUAGE python
  SOURCES "pymatcalc.i" OUTPUT_DIR "${PYMATCALC_DIR}")
target_link_libraries(pymatcalc Python3::Python dylib)
set_target_properties(
  pymatcalc PROPERTIES LIBRARY_OUTPUT_DIRECTORY "$<1:${PYMATCALC_DIR}>"
                       SUFFIX "${EXT_SUFFIX}")
