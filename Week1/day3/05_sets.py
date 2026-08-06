"""
Sets
"""

# Problem 1: Given two lists of student names, find students enrolled in both classes.

def enrolled_in_both(class1: list, class2: list) -> set:
    common_students = set(class1) & set(class2)
    return common_students

# Problem 2: Check if a list has any duplicate values.
def has_duplicates(items: list):
    return len(items) != len(set(items))

# Problem 3: Given two sets of skills required for two jobs, find skills unique to job A only (not needed for job B).
def unique_skills(job_a_skills: set, job_b_skills: set) -> set:
    unique_skills = job_a_skills - job_b_skills
    return unique_skills

# Problem 4: Given a string, find how many unique characters it contains (ignoring case and spaces).
def unique_chars(text: str) -> int:
    unique_chars = len(set(text.lower().replace(" ", "")))
    return unique_chars

# Problem 5: Given two lists of email subscribers, find everyone who is in exactly one list, not both (symmetric difference).
def unique_subscribers(list1: list, list2: list) -> set:
    unique_subscribers = set(list1) ^ set(list2)
    return unique_subscribers

if __name__ == "__main__":
    
    class1 = ["Alice", "Bob", "Charlie"]
    class2 = ["Bob", "Charlie", "David"]
    
    # Problem 1
    common_students = enrolled_in_both(class1, class2)
    print(f"Common students: {common_students}")
    
    # Problem 2
    num_list = [1,2,2,4]
    print(f"Has duplicates: {has_duplicates(num_list)}")
    
    # Problem 3
    job_a_skills = {"Python", "Java", "C++"}
    job_b_skills = {"Java", "C++", "JavaScript"}
    unique_skills = unique_skills(job_a_skills, job_b_skills)
    print(f"Unique skills for job A: {unique_skills}")
    
    # Problem 4
    text = "Hello, World!"
    unique_chars = unique_chars(text)
    print(f"Number of unique characters: {unique_chars}")
    
    # Problem 5
    newsletter_a = ["abc@example.com", "def@example.com", "ghi@example.com"]
    newsletter_b = ["def@example.com", "jkl@example.com"]
    unique_subscribers = unique_subscribers(newsletter_a, newsletter_b)
    print(f"Unique subscribers: {unique_subscribers}")



