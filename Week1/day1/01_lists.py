"""
Lists
"""

# Problem 1: Create a list of 5 fruits and print the list
fruits = ["apple", "banana", "cherry", "date", "elderberry"]
for index, fruit in enumerate(fruits):
    print(index,fruit)
    
# Problem 2: Given a list of numbers, print the new list containing the squares of the numbers
def square_list(numbers):
    squared_numbers = [x*x for x in numbers]
    return squared_numbers

# Problem 3: Given a list of numbers, print the sum and average of the numbers
def sum_and_avg(numbers):
    sum = 0
    for n in numbers:
        sum += n
    avg = sum / len(numbers)
    return sum, avg

# Problem 4: Given a list of numbers, Remove the dupliactes from the list while preserving the order
def remove_duplicates(numbers):
    seen = set() # Sets are unordered collections of unique elements
    unique_numbers = []
    for n in numbers:
        if n not in seen:
            seen.add(n)
            unique_numbers.append(n)
    return unique_numbers

# Problem 5: Given a list of numbers, find the second largest number in the list
def second_largest(numbers):
    numbers.sort(reverse=True)
    if len(numbers) < 2:
        return None
    return numbers[1]

# Problem 6: Given a list of numbers, print the even numbers using list comprehension
def list_comprehension(numbers):
    even_numbers = [ x for x in numbers if x % 2 == 0]
    return even_numbers

if __name__ == "__main__":
    numbers = [1, 3 ,7 , 4 , 2 , 6 , 5, 4, 8, 9, 10]
    
    # Problem 2
    squared_numbers = square_list(numbers)
    print(f"Squared numbers: {squared_numbers}")

    # Problem 3
    sum, avg = sum_and_avg(numbers)
    print(f"Sum: {sum}, Average: {avg}")

    # Problem 4
    unique_numbers = remove_duplicates(numbers)
    print(f"Unique numbers: {unique_numbers}")

    # Problem 5
    second_largest_number = second_largest(numbers)
    print(f"Second largest number: {second_largest_number}")
    
    # Problem 6
    even_numbers = list_comprehension(numbers)
    print(f"Even numbers: {even_numbers}")