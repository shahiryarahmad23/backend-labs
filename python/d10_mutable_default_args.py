import copy

a = [1,2]
a.append(a)
copya = copy.deepcopy(a)

print(copya)

