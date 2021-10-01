#include <iostream>
#include <vector>
#include <string.h>

int main(int argc, char** argv)
{
    if (argc == 1) {
        std::cout << "Hello world!\n"; 
    } else if (argc == 2) {
        std::cout << argv[1] << "\n"; 
    } else {
        return 1;
    }
}