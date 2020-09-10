# GCC settings

## General

We will compile with C++17 without any extensions, so the basic command live will looks like

```
g++ main.cpp -pedantic -std=c++17 -pthread -fmax-errors=3
```

## Warning levels

For compiling of students projects we will us following g++ warning settings. 

```
-Wall -Wextra -Wformat=2 -Wlogical-op -Wmissing-include-dirs -Wredundant-decls -Wsign-conversion -Wstrict-overflow=2 -Wundef -Wnull-dereference -Wuninitialized -Walloca  -Wcast-qual
```

### Additional warnings (possible added throughout semester)

* `-Wold-style-cast` after we discuss what is `static_cast` etc. using old style casts will be forbidden
* `-Wshadow=local` shadowing is not a bug, but more like code smell, so maybe we will use it
* `-Wzero-as-null-pointer-constant` when we start using `nullptr` this will be usefull
* `-Wimplicit-fallthrough=5 ` after we talked about `[[fallthrough]]` attribute in case
* `-Wcast-align=strict` after we forbid use of `malloc`


## Others

By using address sanitization and/or debug containers we can catch a lot of problems in the code without actually reading the code. Changes of false positives in such small programs are almost zero. 

```
-fsanitize=address -D_GLIBCXX_DEBUG
```

Up to debate are `-Wsign-conversion` and `-Wsign-compare` (included in `-Wextra`), since they warn like maniacs on arguably good code. We can manage it by adding `/w44388` and `/w44365` to MSVC compiler, than it will warn on the same places. But quite a lot of standard headers are not compatible with those settings. It is quite hard to set it just for some files, but we may create an template with all of the necesarry stuff...

# Valgrind

Using **Valgrind** will ensure, there are no memory leaks and to some extent races between threads. 

- `valgrind <app>` will check for memory access errors and leaks. (maybe obsolete with `-fsanitize=address` added to build)
- `valgrind --tool=helgrind <app>` will check for races and inconsistencies in locking