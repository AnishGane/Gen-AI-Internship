"""
Collections
"""

from collections import Counter, defaultdict, namedtuple, deque

# Counter.elements() -> returns an iterator over elements, repeating each as many times as its count, count <=0 are excluded.
fruits_count = Counter(apple=10, banana=5, orange=0)
print(list(fruits_count.elements()))

# Counter.most_common() -> Returns a list of (element, count) tuples sorted by count, descending. Pass an optional n to limit to the top n.
votes = Counter(["cat","dog","cat","fish","cat", "dog"])
print(votes.most_common())

# Counter.subtract() -> Subtracts counts, in place, from another iterable or mapping. Counts can go negative (unlike regular dict subtraction).
stock = Counter(apples=10, bananas = 5, oranges = 3)
sold = Counter(apples=5, oranges=7)
stock.subtract(sold)
print(stock)

# Counter.total() -> Returns the sum of all counts.
cart = Counter(apples=10, bananas=5, oranges=3)
print(f"Total count: {cart.total()}")

# Counter.update() -> Adds counts, in place, from another iterable or mapping (opposite of subtract).
daily_visits = Counter(homepage=50, aboutpage=2)
new_visits = ["homepage", "homepage", "homepage", "aboutpage", "contactpage"]

daily_visits.update(new_visits)
print(f"Updated daily_visits: {daily_visits}")

# defaultdict() -> a dict subclass that calls a factory function to supply missing values.
d = defaultdict(int)
for char in "mississippi":
    d[char] += 1
    
print(dict(d))

# namedtuple() -> A factory function that creates a lightweight, immutable tuple subclass with named fields — readable like an object, but as memory-efficient and hashable as a tuple.

Employee = namedtuple("Employee", ["name", "age", "role"])
emp = Employee("John", 30, "Manager")

print(emp.name, emp.age, emp.role)
print(emp[0], emp[2])

# Problem 1: Find the most common word in a paragraph.
text = "python is great and python is fun and python is powerful"
word_counts = Counter(text.split())
print(word_counts.most_common(1))

# Problem 2: Check if two strings are anagrams of each other.
def is_anagram(s1: str, s2: str) -> bool:
    return Counter(s1.replace(" ", "").lower()) == Counter(s2.replace(" ", "").lower())

print(is_anagram("listen", "silent"))
print(is_anagram("hello", "world"))

# Problem 3: Group a list of words by their first letter.
words = ['apple', 'banana', 'cherry', 'date', 'elderberry']
grouped_words = defaultdict(list)

for word in words:
    grouped_words[word[0]].append(word)

print(dict(grouped_words))

# Problem 4: Model a product with name, price, and quantity, then compute total inventory value.
Product = namedtuple('Product', ["name", "price", "quantity"])

inventory = [
    Product("Laptop", 800, 3),
    Product("Phone", 500, 5),
    Product("Tablet", 300, 2)
]

total_value = sum(p.price * p.quantity for p in inventory)
print(f"Total inventory value: {total_value}")

# Problem 5: Simulate a print queue where jobs are processed first-in-first-out, and you can also add urgent jobs to the front.

print_queue = deque(["doc1, doc2, doc3"])

print_queue.append("doc4")
print_queue.appendleft("urgentdoc1")

print(print_queue)

next_job = print_queue.popleft()
print(f"Now printing: {next_job}")