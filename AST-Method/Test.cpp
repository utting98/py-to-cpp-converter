#include <fstream>
#include <vector>
#include <string>
#include <iostream>
class TestObject {
	public:
		std::string name;
		float value;
	auto print_object () {
		std::cout << name << std::endl;
		std::cout << value << std::endl;
		return;
	}
};
auto TestFunction (int a, std::vector<float> b, std::string c, float randfloat) {
	int x_value = a + a;
	float y_value = randfloat / 2;
	std::cout << a << std::endl;
	std::cout << c << randfloat << std::endl;
	struct result {int dummy_return_0; float dummy_return_1;};
	return result {x_value, y_value};
}
int main () {
	int a = 1;
	int e = -2;
	float b = 2.2;
	float f = -3.7;
	std::string c = "Hello";
	std::string d = "World";
	std::vector<float> g = {2.2, 3.3, 4.4};
	std::vector<std::vector<int>> matrix = {{2, 2, 2}, {3, 3, 3}, {4, 4, 4}};
	std::cout << "Hello2" << std::endl;
	std::cout << "Hello3" << std::endl;
	if (a == 1) {
		std::cout << c << std::endl;
		std::cout << d << std::endl;
		if (c == "Hello") {
			std::cout << "Yay" << std::endl;
		}
		else {
			std::cout << "Nay" << std::endl;
		}
	}
	else if (b == 2) {
		std::cout << "Test" << std::endl;
		if (d == "World") {
			std::cout << "Yay 2" << std::endl;
		}
		else {
			std::cout << "Nay 2" << std::endl;
		}
	}
	else {
		

	}
	std::cout << "Extra" << std::endl;
	auto value = TestFunction(a, g, c, b);
	for (int i = 0; i < 5; i++) {
		g[i] = 1.1;
		g.push_back(9.9);
	}
	float test_value = g[1];
	g[1] = 5.1;
	int incrementor = 1;
	bool boolean = true;
	while (incrementor < 10) {
		incrementor += 1;
		break;
	}
	if (boolean == true) {
		std::cout << "False" << std::endl;
	}
	else {
	}
	TestObject object1;
	object1.name = "Object_name";
	object1.value = 7.2;
	object1.print_object();
	for (int i = 0; i < g.size(); i++) {
		std::cout << i << std::endl;
	}
	for (auto element: g) {
		std::cout << element << std::endl;
	}
	TestObject object2;
	object2.name = "Object_name_2";
	object2.value = 3.3;
	object2.print_object();
	TestObject object3;
	object3.name = "New_Name_1";
	object3.value = 1.0;
	object3.print_object();
	for (int i = g.size(); i > 0; i--) {
		std::cout << i << std::endl;
	}
	std::cout << "Enter your age (years): ";
	int convert_input_to_int;
	std::cin >> convert_input_to_int;
	std::cin.get();
	std::cout << std::endl;
	std::cout << convert_input_to_int << std::endl;
	std::cout << "Enter your name: ";
	std::string string_input;
	std::getline (std::cin, string_input);
	std::cout << std::endl;
	std::cout << string_input << std::endl;
	std::vector<std::string> empty_list_dec = {};
	empty_list_dec.push_back("string_to_push_back");
	for (auto i: empty_list_dec) {
		std::cout << i << std::endl;
	}
	std::fstream read_file;
	read_file.open("RWTest.txt",std::ios::in);
	std::vector<std::string> lines = {};
	std::string file_line;
	while (!read_file.eof()) {
		std::getline(read_file,file_line,'\n');
		lines.push_back(file_line);
	}
	read_file.close();
	for (auto i: lines) {
		std::cout << i << std::endl;
	}
	return 0;
}
