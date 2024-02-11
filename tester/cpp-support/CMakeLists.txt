cmake_minimum_required (VERSION 3.16)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(C_STANDARD 17)
set(C_STANDARD_REQUIRED ON)

if(MSVC)
  add_compile_options(/W4)
else()
  add_compile_options(-Wall -Wextra -Wpedantic -Wlogical-op -Wmissing-include-dirs -Wredundant-decls -Wstrict-overflow -Wundef -Wnull-dereference -Walloca $<$<COMPILE_LANGUAGE:CXX>:-Werror=vla>)
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -fsanitize=address,leak -D_GLIBCXX_ASSERTIONS -D_GLIBCXX_DEBUG -D_GLIBCXX_DEBUG_PEDANTIC -D_GLIBCXX_SANITIZE_VECTOR")
  set(CMAKE_LINKER_FLAGS_DEBUG "${CMAKE_LINKER_FLAGS_DEBUG} -fsanitize=address,leak")
endif()

project(apc-tests LANGUAGES C CXX VERSION 1.0.0)

find_package(Catch2 CONFIG REQUIRED)

add_executable(apc-tests "launch.cpp" "main.cpp" "support.c")
target_compile_features(apc-tests PUBLIC cxx_std_20)

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

target_link_libraries(apc-tests PRIVATE Threads::Threads)
target_link_libraries(apc-tests PRIVATE Catch2::Catch2)
