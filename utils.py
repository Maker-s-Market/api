def verify_password(password: str):
    if len(password) < 8 or \
            not any(char.isdigit() for char in password) or \
            not any(char.isupper() for char in password) or \
            not any(char.islower() for char in password) or \
            not any(char in ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '='] for char in password):
        return False
    return True
