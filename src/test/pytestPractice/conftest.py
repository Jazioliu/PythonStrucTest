import pytest


@pytest.fixture(scope='function', autouse=True)
def HiAll():
    print('\nSurprise!!!!')
    yield
    print('\nGoodBye~~~~\n')
