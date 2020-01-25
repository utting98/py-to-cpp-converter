class TestObject:
    def __init__(self,name,value):
        self.name = name
        self.value = value
    def print_object(self):
        print(self.name)
        print(self.value)
def TestFunction(a,b,c,randfloat):
    x_value = a+a
    y_value = randfloat/2
    print(a)
    print(c,randfloat)
    return x_value,y_value
#Test.py
a=1
e=-2
b=2.2
f=-3.7
c='Hello'
d="World"
g=[2.2,3.3,4.4]
matrix=[[2,2,2],[3,3,3],[4,4,4]]
print('Hello2')
print("Hello3")
if(a==1):
    print(c)
    print(d)
    if(c=='Hello'):
        print('Yay')
    else:
        print('Nay')
elif(b==2):
    print("Test")
    if(d=='World'):
        print('Yay 2')
    else:
        print('Nay 2')
else:
    pass
print('Extra')
value = TestFunction(a,g,c,b)
for i in range(0,5):
    g[i] = 1.1
    g.append(9.9)
test_value = g[1]
g[1] = 5.1
incrementor = 1
boolean = True
while(incrementor<10):
    incrementor+=1
    break
if(boolean == True):
    print('False')
object1 = TestObject('Object_name',7.2)
object1.print_object()
for i in range(0,len(g)):
    print(i)
for element in g:
    print(element)
object2 = TestObject('Object_name_2',3.3)
object2.print_object()
object3 = TestObject('New_Name_1',1.0)
object3.print_object()
for i in reversed(range(0,len(g))):
    print(i)
convert_input_to_int = int(input('Enter your age (years): '))
print(convert_input_to_int)
string_input = input('Enter your name: ')
print(string_input)
