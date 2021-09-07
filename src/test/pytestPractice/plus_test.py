def plus_numbers(a, b):
    return a + b


class TestPlusNumbers:
    def testPlusNumbers_Normal(self):
        assert 5 == plus_numbers(3, 2)


def testPlusNumbers_Normal():
    assert 5 == plus_numbers(3, 2)
