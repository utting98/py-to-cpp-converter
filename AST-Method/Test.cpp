#include <vector>
#include <string>
#include <iostream>
auto TestFunction (int a, std::vector<float> b, std::string c, float randfloat) {
	int x_value = a + a;
	float y_value = randfloat / 2;
	std::cout << b << a << endl;
	std::cout << c << randfloat << endl;
	struct result {int dummy_return_0; float dummy_return_1;};
	return result {x_value, y_value};
}
int main() {
	int a = 1;
	int e = -2;
	float b = 2.2;
	float f = -3.7;
	std::string c = "Hello";
	std::string d = "World";
	std::vector<float> g = {2.2, 3.3, 4.4};
	std::vector<std::vector<int>> matrix = {{2, 2, 2}, {3, 3, 3}, {4, 4, 4}};
	std::cout << "Hello2" << endl;
	std::cout << "Hello3" << endl;
	if (a == 1) {
		std::cout << c << endl;
		std::cout << d << endl;
	}
	else if (b == 2) {
		std::cout << "Test" << endl;
	}
	else {
		continue;
	}
	std::cout << "Extra" << endl;
	TestFunction(a, g, c, b);
	for (int i = 0; i < g.size(); i++) {
		g[i] = 1.1;
		g.push_back(9.9);
	}
	float test_value = g[1];
	g[3] = 5.1;
	return 0;
}
