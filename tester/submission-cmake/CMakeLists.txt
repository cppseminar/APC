cmake_minimum_required (VERSION 3.16)

project(apc-submission LANGUAGES CXX VERSION 1.0.0)

add_executable(apc-submission "main.cpp")

# compile as C++20 without any extensions
set_property(TARGET apc-submission PROPERTY CXX_STANDARD 20)
set_property(TARGET apc-submission PROPERTY CXX_STANDARD_REQUIRED ON)
set_property(TARGET apc-submission PROPERTY CXX_CXX_EXTENSIONS OFF)

# enable symbols for debug build, for some reason the default is -g, but
# every time we added something different with target_compile_options it
# just disappeared, strange :(
target_compile_options(apc-submission PRIVATE
  $<$<AND:$<NOT:$<CXX_COMPILER_ID:MSVC>>,$<CONFIG:Debug>>:-g -fno-omit-frame-pointer>
)

# enable warnings
target_compile_options(apc-submission PRIVATE
  $<$<CXX_COMPILER_ID:MSVC>:/W4>
  $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra -Wpedantic -Wlogical-op -Wmissing-include-dirs -Wredundant-decls -Wstrict-overflow -Wundef -Wnull-dereference -Walloca -Werror=vla>
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
