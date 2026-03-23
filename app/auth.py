import json
import os

USER_DB = "data/users.json"

def load_users():
    if not os.path.exists(USER_DB):
        return {}

    try:
        with open(USER_DB, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=4)

def register_user(username, data):
    users = load_users()
    if username in users:
        return False
    users[username] = data
    save_users(users)
    return True

def login_user(username, password):
    users = load_users()
    if username in users and users[username]["password"] == password:
        return users[username]
    return None