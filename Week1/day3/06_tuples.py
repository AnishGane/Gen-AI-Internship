"""
Tuple
"""

import math

# Problem 1: Store a 2D point and calculate the distance from the origin.
def calculate_dist(point):
    x, y = point
    return math.sqrt(x**2 + y**2)

# Problem 2: Use tuples as dictionary keys to store distances between city pairs.
def print_distances(distances):
    for key, value in distances.items():
        print(f"Distance between {key[0]} and {key[1]} is {value} km")
        
# Problem 3: Given a list of (name, score) tuples, sort by score descending.
def sort_scores(students: list):
    ranked = sorted(students, key = lambda x: x[1], reverse=True)
    return ranked

# Problem 4: Swap two variables' values using tuple unpacking (no temp variable).
def swap_variables(a, b):
    a, b = b, a
    return a, b
    

if __name__ == "__main__":
    
    point = (3, 4)
    # Problem 1
    distance = calculate_dist(point)
    print(f"Distance from origin: {distance}")
    
    # Problem 2
    distances = {
        ("A", "B"): 5,
        ("A", "C"): 3,
        ("B", "C"): 2
    }
    print_distances(distances)
    
    # Problem 3
    students = [("Alice", 85), ("Bob", 92), ("Charlie", 78)]
    print(sort_scores(students))
    
    # Problem 4
    a, b = 3, 4
    print(f"Before swap: a = {a}, b = {b}")
    a, b = swap_variables(a, b)
    print(f"After swap: a = {a}, b = {b}")