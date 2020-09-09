# GCC settings

## General

We will compile with C++17 without any extensions, so the basic command live will looks like

```
g++ main.cpp -pedantic -std=c++17 -pthread
```

## Warning levels

For compiling of students projects we will us following g++ warning settings. 

```
-Wall -Wextra -Wctor-dtor-privacy -Wdisabled-optimization -Wformat=2 -Winit-self -Wlogical-op -Wmissing-include-dirs -Wold-style-cast -Woverloaded-virtual -Wredundant-decls -Wshadow -Wsign-conversion -Wsign-promo -Wstrict-null-sentinel -Wstrict-overflow=5 -Wundef -Wno-unused -Wzero-as-null-pointer-constant -fmax-errors=3 -Wnull-dereference -Wimplicit-fallthrough=5 -Wuninitialized -Walloca -Wno-pointer-compare -Wcast-qual -Wcast-align=strict -Wparentheses -Wlogical-op -Wno-multichar -fsanitize=address
```

Up to debate are `-Wsign-conversion` and `-Wsign-compare` (included in `-Wextra`), since they warn like maniacs on arguably good code. We can manage it by adding `/w44388` and `/w44365` to MSVC compiler, than it will warn on the same places. But quite a lot of standard headers are not compatible with those settings. It is quite hard to set it just for some files, but we may create an template with all of the necesarry stuff...

## Valgrind

Using **Valgrind** will ensure, there are no memory leaks and to some extent races between threads. 

- `valgrind <app>` will check for memory access errors and leaks. (maybe obsolete with `-fsanitize=address` added to build)
- `valgrind --tool=helgrind <app>` will check for races and inconsistencies in locking