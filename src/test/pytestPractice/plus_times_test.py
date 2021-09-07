def plus_numbers(a, b):
    return a + b


def times_numbers(a, b):
    return a * b


def testPlusNumbersTimesNumbers_Normal():
    assert 11 == plus_numbers(3, 2) + times_numbers(3, 2)
