

def check_sku(l1,l2):
    
    if len(l1) != len(l2):
        return False
    sorted_l1 = []
    sorted_l2 = []

    for i in range(len(l1)):
        sorted_l1.append(sorted(l1[i]))
        sorted_l2.append(sorted(l2[i]))
            

    if sorted(sorted_l1) == sorted(sorted_l2):  
        return True
    else:
        return False
    

if __name__ == "__main__":
    l1 = ["", "ABC", ""]
    l2 = ["ABC", "", ""]
    print(check_sku(l1,l2))