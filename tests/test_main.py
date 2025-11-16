import pytest
from src.main import is_palindrome


class TestIsPalindrome:
    def test_basic(self):
        assert is_palindrome("kajak") == True

    def test_whitespace_and_case(self):
        assert is_palindrome("Kobyła ma mały bok") == True

    def test_false(self):
        assert is_palindrome("python") == False

    def test_empty(self):
        assert is_palindrome("") == True

    def test_single(self):
        assert is_palindrome("A") == True
