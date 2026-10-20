cmake_minimum_required(VERSION 4.2)

# Enable `import std;` using the same libc++ module metadata as submissions.
set(CMAKE_EXPERIMENTAL_CXX_IMPORT_STD "d0edc3af-4c50-42ea-a356-e2862fe7a444")
set(CMAKE_CXX_STDLIB_MODULES_JSON "/usr/lib/llvm-22/lib/libc++.modules.json")
set(CMAKE_CXX_EXTENSIONS OFF)

set(C_STANDARD 17)
set(C_STANDARD_REQUIRED ON)

if(MSVC)
  add_compile_options(/W4)
else()
  add_compile_options(-Wall -Wextra -Wpedantic -Wmissing-include-dirs -Wredundant-decls -Wstrict-overflow -Wundef -Wnull-dereference -Walloca $<$<COMPILE_LANGUAGE:CXX>:-Werror=vla>)
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -fsanitize=address,leak -D_GLIBCXX_ASSERTIONS -D_GLIBCXX_DEBUG -D_GLIBCXX_DEBUG_PEDANTIC -D_GLIBCXX_SANITIZE_VECTOR")
  set(CMAKE_LINKER_FLAGS_DEBUG "${CMAKE_LINKER_FLAGS_DEBUG} -fsanitize=address,leak")
endif()

project(apc-tests LANGUAGES C CXX VERSION 1.0.0)

find_package(Catch2 CONFIG REQUIRED)

add_executable(apc-tests "launch.cpp" "main.cpp" "support.c")
set_property(TARGET apc-tests PROPERTY CXX_STANDARD 23)
set_property(TARGET apc-tests PROPERTY CXX_STANDARD_REQUIRED ON)
set_property(TARGET apc-tests PROPERTY CXX_EXTENSIONS OFF)
set_property(TARGET apc-tests PROPERTY CXX_SCAN_FOR_MODULES ON)
set_property(TARGET apc-tests PROPERTY CXX_MODULE_STD ON)

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

target_link_libraries(apc-tests PRIVATE Threads::Threads)
target_link_libraries(apc-tests PRIVATE Catch2::Catch2)
