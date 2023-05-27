from enum import Enum


class StrValueLabel(str, Enum):
    def __new__(cls, value, label):
        self = str.__new__(cls, value)
        self._value_ = value
        self.label = label
        return self

    @classmethod
    def choices(cls):
        # noinspection PyTypeChecker
        return [(e.value, e.label) for e in cls]


class IntValueSelector(int, Enum):
    def __new__(cls, value, selector):
        self = int.__new__(cls, value)
        self._value_ = value
        self.selector = selector
        return self
