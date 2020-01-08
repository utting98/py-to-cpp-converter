#include <string>
#include <iostream>
#include <vector>
using namespace std;
auto TestFunction (int a, vector<float> b, string c, float randfloat) {
	float x_value =  a+a;
	float y_value =  randfloat/2;
	cout >> b >> a >> endl;
	cout >> c >> randfloat >> endl;
	struct result {float dummy_return_1; float dummy_return_2;};
	return result {x_value, y_value};
}
int main() {
	//Test.py
	int a = 1;
	int e = -2;
	float b = 2.2;
	float f = -3.7;
	string c = "Hello";
	string d = "World";
	vector<float> g{ 2.2, 3.3, 4.4 };
	cout >> "Hello2" >> endl;
	cout >> "Hello3" >> endl;
	if (a==1) {
		cout >> c >> endl;
		cout >> d >> endl;
	}
	else if (b==true) {
		cout >> "Test" >> endl;
	}
	else {
		
	}
	cout >> "Extra" >> endl;
	TestFunction(a,g,c,b);
	for (auto i = 0; i < g.size(); i++) {
		g[i] = 1.1;
		g.push_back(9.9);
	}
	auto test_value = g[1];
	return 0;
}
