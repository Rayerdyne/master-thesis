#include <iostream>

#include "external.h"

int main() {
    std::cout << "Test dll.cpp" << std::endl;
    std::cout << "a val: " << compute_a(1, 1, 1) << std::endl;

    // float f = super_function(3.0F);
    // std::cout << "Result: " << f << std::endl;
    return 0;
}