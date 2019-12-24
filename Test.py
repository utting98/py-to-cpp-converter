def TestFunction(a,b,c,randfloat):
    x_value = a+a
    y_value = randfloat/2
    print(b,a)
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
print('Hello2')
print("Hello3")
if(a==1):
    print(c)
    print(d)
elif(b==True):
    print("Test")
else:
    pass
print('Extra')
TestFunction(a,g,c,b)
for i in range(0,len(g)):
    g[i] = 1.1
    g.append(9.9)
test_value = g[1]