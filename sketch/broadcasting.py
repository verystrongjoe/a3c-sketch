import  numpy  as np

a = np.array([1.0, 2.0, 3.0])
b = np.array([1.0, 2.0, 3.0])
c = np.array([2.0, 4.0, 6.0])


print((a+b+c)/3)

l = []
l.append(a)
l.append(b)
l.append(c)
print(l)
print(np.mean(l, axis=0))

