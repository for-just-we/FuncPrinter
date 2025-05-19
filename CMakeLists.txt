cmake_minimum_required(VERSION 3.23)
project(FuncPrinter)

set(CMAKE_CXX_STANDARD 17)

find_package(LLVM REQUIRED CONFIG HINTS ${LLVM_DIR})
find_package(Clang REQUIRED CONFIG)
message(STATUS "Found LLVM ${LLVM_PACKAGE_VERSION}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")
list(APPEND CMAKE_MODULE_PATH "${LLVM_CMAKE_DIR}")
include(AddLLVM)

message("LLVM STATUS:
  Definitions ${LLVM_DEFINITIONS}
  Includes    ${LLVM_INCLUDE_DIRS}
  Libraries   ${LLVM_LIBRARY_DIRS}"
        )

add_definitions(${LLVM_DEFINITIONS})
include_directories(SYSTEM ${LLVM_INCLUDE_DIRS})
message(STATUS "Looking for headers in: ${LLVM_INCLUDE_DIRS}")
link_directories(${LLVM_LIBRARY_DIRS})
message(STATUS "Looking for libraries in: ${LLVM_LIBRARY_DIRS}")

if (NOT ${LLVM_ENABLE_RTTI})
    message(STATUS "close rtti")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-rtti")
endif()

if(LLVM_LINK_LLVM_DYLIB)
    message(STATUS "Linking to LLVM dynamic shared library object")
    set(llvm_libs LLVM)
else()
    message(STATUS "Linking to separate LLVM static libraries")
    llvm_map_components_to_libnames(llvm_libs
            ${LLVM_TARGETS_TO_BUILD}
            core support option windowsdriver frontendopenmp mc
            )
endif()

message(STATUS "llvm libs: ${llvm_libs}")

## ZSTD
if(DEFINED zstd_ROOT)
    message("searching ZSTD in: ${zstd_ROOT}")
    # If ZSTD_PATH is defined, look for zstd in that directory
    find_library(ZSTD_LIBRARIES NAMES zstd HINTS ${zstd_ROOT}/lib)
else()
    # If ZSTD_PATH is not defined, look for zstd in system paths
    find_library(ZSTD_LIBRARIES NAMES zstd)
endif()
message(STATUS "find zstd lib: ${ZSTD_LIBRARIES}")
message(STATUS "find zstd include: ${ZSTD_INCLUDE_DIRS}")


add_executable(FuncPrinter FuncPrinter.cpp)

target_link_libraries(FuncPrinter
     ${llvm_libs}
     clangAST
     clangBasic
     clangDriver
     clangFrontend
     clangIndex
     clangLex
     clangSema
     clangSerialization
     clangTooling
     clangFormat
     clangToolingInclusions
     clangToolingCore
     clangRewriteFrontend
     clangStaticAnalyzerFrontend
     clangCrossTU
     clangStaticAnalyzerCheckers
     clangStaticAnalyzerCore
     clangParse
     clangEdit
     clangRewrite
     clangAnalysis
     clangASTMatchers
     clangTransformer
     ${ZSTD_LIBRARIES})