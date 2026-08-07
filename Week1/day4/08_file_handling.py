"""
File Handling
"""
import os
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Problem 1: Write some contents in the file named "sample.txt" in data folder
def write_content(file_path: str, content: str):
    with open(file_path, "w") as f:
        f.write(content)
    print(f"Content written to {file_path}")

# Problem 2: Read a file,and print its contents
def read_file(file_path: str):
    with open(file_path, "r") as f:
        print(f"Contents of {file_path}: {f.read()}")
        
# Problem 3: Write a list of names to a text file, one per line
def write_names(file_path: str, names: list): 
    with open(file_path, "w") as f:
        for name in names:
            f.write(f"{name}\n")
    print(f"Names written to {file_path}")

# Problem 4: Save dictionary as JSON file
def save_json(file_path: str, data: dict):
    with open(file_path, "w") as f:
        json.dump(data, f)
        
    print(f"Data saved to {file_path}")
    
# Problem 5: Load the JSON file back into a dictionary
def load_dict(file_path: str):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

if __name__ == "__main__":
    # Problem 1
    file_path = os.path.join(DATA_DIR, "sample.txt")
    write_content(file_path, "Hello, World!")
    
    # Problem 2
    read_file(file_path)
    
    # Problem 3
    names = ["John", "Alice", "Bob"]
    write_names(os.path.join(DATA_DIR, "names.txt"), names)
    
    # Problem 4
    data = {"name": "John", "age": 30, "city": "New York"}
    save_json(os.path.join(DATA_DIR, "profile.json"), data)
    
    # Problem 5
    data = load_dict(os.path.join(DATA_DIR, "profile.json"))
    print(data)