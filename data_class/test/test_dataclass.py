import pytest

from data_class.model import Name, Money, Line, Person


@pytest.fixture
def monies():
    return Money("gdp", 5), Money("gdp", 10)


def test_equility():
    assert Money("gdp", 10) == Money("gdp", 10)
    assert Name("Harry", "Percival") != Name("Bob", "Geogry")
    assert Line("RED-CHAIR", 10) == Line("RED-CHAIR", 10)


def test_can_add_money_values_for_the_same_currency(monies):
    fiver, tenner = monies
    assert fiver + fiver == tenner


def test_can_subtract_money_values(monies):
    fiver, tenner = monies
    assert tenner - fiver == fiver


def test_adding_different_currencies_fails(monies):
    with pytest.raises(ValueError):
        Money("usd", 10) + Money('gdp', 10)


def test_can_multiply_money_by_a_number(monies):
    fiver, _ = monies
    assert fiver * 5 == Money("gdp", 25)


def test_multiplying_two_money_values_is_an_error(monies):
    fiver, tenner = monies
    with pytest.raises(TypeError):
        fiver * tenner


def test_barry_is_harry():
    harry = Person(Name("Harry", "Percival"))
    barry = harry

    barry.name = Name("Barry", "percival")

    assert harry is barry and barry is harry

