import pytest
from src.main import (
    is_palindrome,
    fibonacci,
    count_vowels,
    calculate_discount,
    flatten_list,
    word_frequencies,
    is_prime
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


class TestFlattenList:
    def test_flat(self):
        assert flatten_list([1, 2, 3]) == [1, 2, 3]

    def test_basic(self):
        assert flatten_list([1, [2, 3], [4, [5]]]) == [1, 2, 3, 4, 5]

    def test_empty(self):
        assert flatten_list([]) == []
    
    def test_single_nested(self):
        assert flatten_list([[[1]]]) == [1]

    def test_basic2(self):
        assert flatten_list([1,[2,[3,[4]]]]) == [1,2,3,4]


class TestWordFrequencies:
    def test_to_be(self):
        assert word_frequencies("To be or not to be") == {"to": 2, "be": 2, "or": 1, "not": 1}

    def test_hello_world(self):
        assert word_frequencies("Hello world") == {"hello": 1, "world": 1}

    def test_empty(self):
        assert word_frequencies("") == {}

    def test_triple_python(self):
        assert word_frequencies("Python Python python") == {"python": 3}

    def test_ala_ma_kota(self):
        assert word_frequencies("Ala ma kota, a kot ma Ale.") == {"ala": 1, "ma": 2, "kota": 1, 'a': 1, 'kot': 1, 'ale': 1}


class TestIsPrime:
    def test_two(self):
        assert is_prime(2) == True

    def test_three(self):
        assert is_prime(3) == True

    def test_four(self):
        assert is_prime(4) == False

    def test_zero(self):
        assert is_prime(0) == False
    
    def test_one(self):
        assert is_prime(1) == False
    
    def test_five(self):
        assert is_prime(5) == True
    
    def test_97(self):
        assert is_prime(97) == True