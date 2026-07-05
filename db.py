users = []

def create_user(user, password, expire):
    users.append({
        "user": user,
        "password": password,
        "expire": expire
    })

def get_users():
    return users