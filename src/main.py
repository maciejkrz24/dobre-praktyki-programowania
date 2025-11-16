# 1. is_palindrome(text: str) -> bool - sprawdza, czy dany ciąg znaków jest palindromem (ignorując wielkość liter i spacje).
def is_palindrome(text: str) -> bool:
    return text.lower().replace(" ", "") == text[::-1].lower().replace(" ", "")

# 2. fibonacci(n: int) -> int - zwraca n-ty element ciągu Fibonacciego (Załóż, że fibonacci(0) == 0, fibonacci(1) == 1).
def fibonacci(n: int) -> int:
    if n == 0:
        return 0
    elif n == 1:
        return 1
    elif n < 0:
        raise ValueError("n must be non-negative")
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)

# 3. count_vowels(text: str) -> int - zlicza liczbę samogłosek w podanym ciągu (a, e, i, o, u, y – wielkość liter bez znaczenia).
def count_vowels(text: str) -> int:
    return sum(1 for char in text.lower() if char in 'aeiouóyęą')

# 4. calculate_discount(price: float, discount: float) -> float - zwraca cenę po uwzględnieniu zniżki (np. calculate_discount(100, 0.2) → 80).  Jeśli discount jest spoza zakresu 0–1, ma zostać zgłoszony wyjątek ValueError.
def calculate_discount(price: float, discount: float) -> float:
    if discount < 0 or discount > 1:
        raise ValueError("Discount must be between 0 and 1")
    return price - price * discount

# 5. flatten_list(nested_list: list) -> list - przyjmuje listę (mogącą zawierać zagnieżdżone listy) i zwraca ją „spłaszczoną”.  Przykład: [1, [2, 3], [4, [5]]] → [1, 2, 3, 4, 5]
def flatten_list(nested_list: list) -> list:
    return [item for sublist in nested_list for item in sublist]

# 6. word_frequencies(text: str) -> dict - zwraca słownik z częstością występowania słów w tekście (ignorując wielkość liter i interpunkcję).
def word_frequencies(text: str) -> dict:
    return {word.lower(): text.lower().count(word.lower()) for word in text.split()}

# 7. is_prime(n: int) -> bool - sprawdza, czy liczba jest pierwsza.  Jeśli n < 2, zwraca False.
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True