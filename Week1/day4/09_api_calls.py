"""
Calling an API with 'requests' and reading JSON
"""

import requests

BASE_URL = 'https://jsonplaceholder.typicode.com'

# Problem 1: Get a single user by userId and return the parsed JSON as dict
def get_user(user_id):
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    response.raise_for_status() # It raises an error if the request fails
    return response.json()

# Problem 2: Get all posts written by a user and return the parsed JSON as list
def get_posts_by_user(user_id):
    response = requests.get(f"{BASE_URL}/users/{user_id}/posts")
    response.raise_for_status()
    return response.json()

# Problem 3: POST a new post
def create_post(title, body, user_id):
    payload = {
        "title": title,
        "body": body,
        "userId": user_id
    }
    response = requests.post(f"{BASE_URL}/posts", json=payload)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":

    user_id = 1

    # Problem 1
    user = get_user(user_id)
    print(f"User: {user['name']} ({user['email']})")

    # Problem 2
    posts = get_posts_by_user(user_id)
    print(f"Posts by {user['name']}:")
    for post in posts:
        print(f"- {post['title']}")
        
    # Problem 3
    title = "New Post"
    body = "This is a new post."
    new_post = create_post(title, body, user_id)
    print(f"New post created: {new_post['title']}")