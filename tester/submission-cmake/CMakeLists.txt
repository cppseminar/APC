cmake_minimum_required(VERSION 4.2)

# allow import std;
set(CMAKE_EXPERIMENTAL_CXX_IMPORT_STD "d0edc3af-4c50-42ea-a356-e2862fe7a444")
set(CMAKE_CXX_STDLIB_MODULES_JSON "/usr/lib/llvm-22/lib/libc++.modules.json")
set(CMAKE_CXX_EXTENSIONS OFF)

project(apc-submission LANGUAGES CXX VERSION 1.0.0)

add_executable(apc-submission "main.cpp")

# compile as C++23 without any extensions and enable import std
set_property(TARGET apc-submission PROPERTY CXX_STANDARD 23)
set_property(TARGET apc-submission PROPERTY CXX_STANDARD_REQUIRED ON)
set_property(TARGET apc-submission PROPERTY CXX_EXTENSIONS OFF)
set_property(TARGET apc-submission PROPERTY CXX_SCAN_FOR_MODULES ON)
set_property(TARGET apc-submission PROPERTY CXX_MODULE_STD ON)

# enable symbols for debug build, for some reason the default is -g, but
# every time we added something different with target_compile_options it
# just disappeared, strange :(
target_compile_options(apc-submission PRIVATE
  $<$<AND:$<NOT:$<CXX_COMPILER_ID:MSVC>>,$<CONFIG:Debug>>:-g -fno-omit-frame-pointer>
)

# enable warnings
target_compile_options(apc-submission PRIVATE
  $<$<CXX_COMPILER_ID:MSVC>:/W4>
  $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra -Wpedantic -Wmissing-include-dirs -Wredundant-decls -Wstrict-overflow -Wundef -Wnull-dereference -Walloca -Werror=vla>
  $<$<CXX_COMPILER_ID:GNU>:-Wlogical-op>
)

# enable sanitizers and debug containers
target_compile_options(apc-submission PRIVATE
  $<$<AND:$<NOT:$<CXX_COMPILER_ID:MSVC>>,$<CONFIG:Debug>>:-fsanitize=address,leak -D_GLIBCXX_ASSERTIONS -D_GLIBCXX_DEBUG -D_GLIBCXX_DEBUG_PEDANTIC -D_GLIBCXX_SANITIZE_VECTOR>
)

target_link_options(apc-submission PRIVATE
  $<$<AND:$<NOT:$<CXX_COMPILER_ID:MSVC>>,$<CONFIG:Debug>>:-fsanitize=address,leak>
)

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

target_link_libraries(apc-submission PRIVATE Threads::Threads)

# print some message to ease debugging
message(STATUS "Compiler path: ${CMAKE_CXX_COMPILER}")
message(STATUS "Compiler ID: ${CMAKE_CXX_COMPILER_ID}")
message(STATUS "Compiler version: ${CMAKE_CXX_COMPILER_VERSION}")
message(STATUS "Compiler is part of GCC: ${CMAKE_COMPILER_IS_GNUCXX}")

get_target_property(COMPILE_OPTS apc-submission COMPILE_OPTIONS)
message(STATUS "App compile definitions are ${COMPILE_OPTS}")
