import unittest

from fastapi import HTTPException

from utils import verify_password


class TestVerifyPassword(unittest.TestCase):
    def test_valid_password(self):
        password = "Abcdefg1@"
        result = verify_password(password)
        self.assertTrue(result)

    def test_password_too_short(self):
        password = "Abc123@"
        result = verify_password(password)
        self.assertFalse(result)

    def test_password_no_digit(self):
        password = "Abcdefg@"
        result = verify_password(password)
        self.assertFalse(result)

    def test_password_no_uppercase(self):
        password = "abcdefg1@"
        result = verify_password(password)
        self.assertFalse(result)

    def test_password_no_lowercase(self):
        password = "ABCDEFG1@"
        result = verify_password(password)
        self.assertFalse(result)

    def test_password_no_special_character(self):
        password = "Abcdefg1"
        result = verify_password(password)
        self.assertFalse(result)
