from http.client import HTTPException


def verify_password(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=500, detail="Password must have at least 8 characters")
    elif not any(char.isdigit() for char in password):
        raise HTTPException(status_code=500, detail="Password must have at least one digit")
    elif not any(char.isupper() for char in password):
        raise HTTPException(status_code=500, detail="Password must have at least one uppercase letter")
    elif not any(char.islower() for char in password):
        raise HTTPException(status_code=500, detail="Password must have at least one lowercase letter")
    elif not any(
            char in ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '='] for char in password):
        raise HTTPException(status_code=500, detail="Password must have at least one special character")
    return True
