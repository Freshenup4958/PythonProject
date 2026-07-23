def string_length(text):
    return len(text)
print(string_length("have a good day"))

def join_strings(first,second):
    return first+second
print(join_strings("hello","world"))

def square_number(n):
    return n*n
print(square_number(7))

def add_numbers(a,b):
    return a+b
print(add_numbers(9,8))

def divide_numbers(a,b):
    return a//b,a%b
print(divide_numbers(77, 3))

def average_of_numbers(numbers):
    return sum(numbers)/len(numbers)
print(average_of_numbers([1,4,3,5,5,6,8]))

def list_of_numbers(n,b):
    return [x for x in b if x in n]
print(list_of_numbers([1,2,5,6,7],[1,3,5,8,9]))

def print_keys(dictionary):
    for key in dictionary:
     print(key)
student ={
        "name" : "Barak Obama",
        "age" : "14",
        "birthday": "25.07"
}
print_keys(student)

def dictionaries(dictionary1, dictionary2):
    return dictionary1 | dictionary2
dictionary1 ={
    "name" : "Barak Obama",
    "age" : "14"
}
dictionary2 ={
    "city":"Krakov",
    "country":"Poland"
}
print(dictionaries(dictionary1,dictionary2))

def union_sets(set1,set2):
    return set1 | set2
print(union_sets({1,2,5,7},{1,3,4,5,6}))

def chek_sets(set1,set2):
    return set1.issubset(set2)
print(chek_sets({1,2,3},{1,2,3,4,5}))

def function(num1):
    return "Парне" if num1 % 2 ==0 else "Непарне"
print(function(5))
print(function(6))

def only_even(numbers):
    return [x for x in numbers if x % 2 == 0]
print(only_even([1,2,3,4,5,6]))

even_odd = lambda x: "Парне" if x % 2 ==0 else "Непарне"
print(even_odd(1))
