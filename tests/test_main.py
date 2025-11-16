import pytest
from src.main import (
    is_palindrome,
    fibonacci,
    count_vowels,
    calculate_discount
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


class TestCountVowels:
    def test_basic(self):
        assert count_vowels("Python") == 2

    def test_all_vowels(self):
        assert count_vowels("AEIOUY") == 6

    def test_bcd(self):
        assert count_vowels("bcd") == 0

    def test_empty(self):
        assert count_vowels("") == 0

    def test_polish(self):
        assert count_vowels("Próba żółwia") == 5


class TestCalculateDiscount:
    def test_basic(self):
        assert calculate_discount(100, 0.2) == 80.0

    def test_zero_discount(self):
        assert calculate_discount(50, 0) == 50.0

    def test_one_discount(self):
        assert calculate_discount(200, 1) == 0.0

    def test_negative_discount(self):
        with pytest.raises(ValueError):
            calculate_discount(100, -0.1)

    def test_discount_out_of_range(self):
        with pytest.raises(ValueError):
            calculate_discount(100, 1.5)