def duplicate_check(ids:list):
    check = set()
    if len(ids) == 0 or len(ids) == 1:
        return False
    
    for i in ids:
        if i in check:
            return True
        else:
            check.add(i)
    return False

def return_dup(ids:list):
    check = {}
    result = []
    if len(ids) == 0 or len(ids) == 1:
        return False
    
    for i in ids:
        if i in check:
            check[i] = check.get(i) + 1
        else:
            check[i] = 1
    for key,value in check.items():
        if value > 1:
            result.append(key)
    
    if len(result) == 0:
        return False
    else:
        return True,result
    
    


if __name__ == "__main__":
    
    l1 = ["a","b","c"]
    
    print(return_dup(l1))