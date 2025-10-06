#include <iostream>
#include <string>

int main() {
    std::cout << "Hello, World!" << std::endl;

    std::string name;
    std::cout << "Enter your name: ";
    std::getline(std::cin, name);
    std::cout << "Hello, " << name << "! Welcome to UMLC!" << std::endl;

    return 0;
}
