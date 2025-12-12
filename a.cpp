#include <iostream>
#include <string>
#include <unordered_set>

int main() {
    int n;
    std::cin >> n;
    std::unordered_set<std::string> uniq;
    std::string s;
    for (int i = 0; i < n; ++i) {
        std::cin >> s;
        uniq.insert(s);
    }
    std::cout << uniq.size() << "\n";
    return 0;
}