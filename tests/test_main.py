import pytest
from src.main import (
    is_palindrome,
    fibonacci
)


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


class TestFibonacci:
    def test_zero(self):
        assert fibonacci(0) == 0

    def test_one(self):
        assert fibonacci(1) == 1

    def test_five(self):
        assert fibonacci(5) == 5

    def test_ten(self):
        assert fibonacci(10) == 55

    def test_negative(self):
        with pytest.raises(ValueError):
            fibonacci(-1)
