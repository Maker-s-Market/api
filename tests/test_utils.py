import unittest
import os

from fastapi import HTTPException
from utils import verify_password
from dotenv import load_dotenv

load_dotenv()


class TestVerifyPassword(unittest.TestCase):

    def test_valid_password(self):
        password = os.getenv("PASSWORD_CORRECT")
        result = verify_password(password)
        self.assertTrue(result)

    def test_password_too_short(self):
        password = os.getenv("PASSWORD_CORRECT")[0:7]
        result = verify_password(password)
        self.assertFalse(result)

    def test_password_no_digit(self):
        password = ''.join([i for i in os.getenv("PASSWORD_CORRECT") if not i.isdigit()])
        result = verify_password(password)
        self.assertFalse(result)

    def test_password_no_uppercase(self):
        password = os.getenv("PASSWORD_CORRECT").lower()
        result = verify_password(password)
        self.assertFalse(result)

    def test_password_no_lowercase(self):
        password = os.getenv("PASSWORD_CORRECT").upper()
        result = verify_password(password)
        self.assertFalse(result)

    def test_password_no_special_character(self):
        password = os.getenv("PASSWORD_CORRECT").replace('!', '1')
        result = verify_password(password)
        self.assertFalse(result)
