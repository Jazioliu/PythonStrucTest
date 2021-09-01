import pytest


def times_numbers(a, b):
    return a * b

@pytest.mark.parametrize("a,b", [(2, 3), (1, 6)])
def testTimes_Normal(a, b):
    assert 6 == times_numbers(a, b)

def testTimes_Abnormal():
    assert 7 != times_numbers(3, 2)
