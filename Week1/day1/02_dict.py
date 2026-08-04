"""
Dictionaries
"""

# Problem 1: Create a dictionary of 5 fruits and their prices
def create_fruit_dict():
    fruit_dict = {
        "apple": 10,
        "banana": 20,
        "cherry": 30,
        "date": 40,
        "elderberry": 50
    }
    
    return fruit_dict

# Problem 2: Count how many times each word appears in a sentence
def count_words(sentence):
    count_dict = {}
    words = sentence.split()
    for word in words:
        if word in count_dict:
            count_dict[word] += 1
        else:
            count_dict[word] = 1
    return count_dict

# Problem 3: Given a dictionay of students and their scores, print the student with the highest score
def highest_score(student_scores):
    return max(student_scores.items(), key=lambda x: x[1]) 

# Problem 4: Given a 2 dictionaries, merge them into a single dictionary if the keys are the same, add the values
def merge_and_add(dict1, dict2):
    merged_dict = dict1.copy()
    for key, value in dict2.items():
        if key in merged_dict:
            merged_dict[key] += value
        else:
            merged_dict[key] = value
    return merged_dict

# Problem 5: Invert a dictionary (swap keys and values)
def invert_dictionary(dictionary):
    inverted_dict = {value: key for key, value in dictionary.items()}
    return inverted_dict

if __name__ == "__main__":
    sentence = "Hello, how are you? I am fine, thank you."
    
    student_scores = {
        "Kiran": 85,
        "Maira": 90,
        "Ram": 75,
        "Prashil": 80
    }
    
    dict1={
        "Soap": 85,
        "Shampoo": 90,
        "Toothpaste": 75,
        "Toothbrush": 80
    }
    
    dict2={
        "Soap": 10,
        "Shampoo": 20,
    }
    
    # Problem 1
    fruit_dict = create_fruit_dict()
    print(f"Fruit dictionary: {fruit_dict}")
    
    # Problem 2
    count_dict = count_words(sentence)
    print(f"Count dictionary: {count_dict}")

    # Problem 3
    highest_score = highest_score(student_scores)
    print(f"Highest score: {highest_score}")
    
    # Problem 4
    merged_dict = merge_and_add(dict1, dict2)
    print(f"Merged dictionary: {merged_dict}")

    # Problem 5
    inverted_dict = invert_dictionary(dict1)
    print(f"Inverted dictionary: {inverted_dict}")