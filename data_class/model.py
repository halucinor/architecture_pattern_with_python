from dataclasses import dataclass
from typing import NamedTuple
from collections import namedtuple


@dataclass(frozen=True)
class Name:
    first_name: str
    surname: str


class Money(NamedTuple):
    currency: str
    value: int

    def __add__(self, other):
        if self.currency == other.currency:
            return Money(self.currency, self.value + other.value)
        else:
            raise ValueError

    def __sub__(self, other):
        if self.currency == other.currency:
            return Money(self.currency, abs(self.value - other.value))
        else:
            raise ValueError

    def __mul__(self, other: int):
        if type(other) is int:
            return Money(self.currency, self.value * other)
        else:
            raise TypeError


Line = namedtuple("Line", ["sku", 'qty'])


class Person:
    def __init__(self, name: Name):
        self.name = name
