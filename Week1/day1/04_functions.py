"""
Functions
"""

# Problem 1: Write a function to check if the given string is palindrome or not.
def check_palindrome(text: str) -> bool:
    cleaned = text.lower().replace(" ", "")
    return cleaned == cleaned[::-1]

# Problem 2: Write a function with a default argument that greets a person.
def greet(name: str = "Anish") -> str:
    print(f"Hello, {name}")
    
# Problem 3: Write a function that takes any number of arguments and returns their sum.
def sum_numbers(*args: int) -> int:
    return sum(args)

# Problem 4: Write a function that takes keyword arguments and returns a dictionary.
def create_dict(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    # Problem 1
    text = "racecar"
    print(f"Is {text} a palindrome? {check_palindrome(text)}")

    # Problem 2
    greet()

    # Problem 3
    numbers = [1, 2, 3, 4, 5]
    print(f"Sum of {numbers} is {sum_numbers(*numbers)}")
    
    # Problem 4
    create_dict(name="John", age=30, city="New York")