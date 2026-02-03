
def remove_items(my_list):
    new_list = [1, 2]
    return new_list

def add_items(my_list):
    my_list.append(4)
    my_list.append(5)


def main():
    my_list = [1, 2, 3]
    print(my_list)
    add_items(my_list)
    print(my_list)
    my_list = remove_items(my_list)
    print(my_list)
    
main()