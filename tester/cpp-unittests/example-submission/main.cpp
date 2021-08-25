#include <iostream>
#include <vector>
#include <string.h>

int main(int argc, char** argv)
{
    int i;

    if (argc + 1 <= 2) {
        std::cout << "Hello world!\n";
        return 0;
    } 

    if (!strcmp(argv[1], "leak")) {
        new char;
        return 0;
    }

    if (!strcmp(argv[1], "addr")) {
        char s[1] = {};
        s[2] = 0;
        std::cout << s[0];
        return 0;
    }

    if (!strcmp(argv[1], "addr2")) {
        char* s = new char[10]{};
        s[10] = 0;
        std::cout << s[0];
        return 0;
    }

    if (!strcmp(argv[1], "dbg")) {
        std::vector<int> v;
        v.reserve(100);
        v[10] = 0;
        return 0;
    }

    if (!strcmp(argv[1], "abort")) {
        abort();
    }

    if (!strcmp(argv[1], "afterfree")) {
        char *c = new char;
        delete c;
        std::cout << c;
        return 0;
    }

    if (!strcmp(argv[1], "fail")) {
        return 1;
    }  

    if (!strcmp(argv[1], "unhandled")) {
        throw 1;
    }

    if (!strcmp(argv[1], "bench")) {
        int n = 0;
        for (int i = 0; i <= 100; ++i) {
            n += i;
        }
        std::cout << n;
        return 0;
    }

    return 0;
}