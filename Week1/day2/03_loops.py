"""
Loops
"""

# Problem 1: Print the factorial of a number using loop
def print_factorial(n):
    result = 1
    if n == 0 or n == 1:
        return result
    else:
        for i in range(1, n+1):
            result *= i
        return result
    
# Problem 2: Check whether a number is prime
def check_prime(n):
    if n <=1:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True

# Problem 3: Given a string, count the vowels in it using a loop
def check_vowels(text):
    vowels = ["a", "e", "i", "o", "u", "A", "E", "I", "O", "U"]
    count = 0
    for char in text:
        if char in vowels:
            count += 1
    return count

if __name__ == "__main__":
    # Problem 1
    number = 5
    print(f"Factorial of {number} is {print_factorial(number)}")
    
    # Problem 2
    number = 7
    print(f"Is {number} prime? {check_prime(number)}")
    
    # Problem 3
    text = "Hello, World!"
    print(f"Number of vowels in {text} is {check_vowels(text)}")

