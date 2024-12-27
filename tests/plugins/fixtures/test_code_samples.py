"""Fixtures de code pour les tests de plugins."""

COMPLEX_CODE = """
def very_complex_function(x, y):
    result = 0
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                for j in range(y):
                    if j % 3 == 0:
                        result += i * j
                    else:
                        result -= i * j
            else:
                result += i * y
    return result

def simple_function():
    return 42
"""

TEST_FILE_CODE = """
def test_something():
    assert True

def test_another_thing():
    value = calculate_something()
    assert value == expected_value
"""

INVALID_CODE = """
def broken_function(
    # Syntaxe invalide
    return None
""" 