from enum import Enum


class StrValueLabel(str, Enum):
    def __new__(cls, value, label):
        self = str.__new__(cls, value)
        self._value_ = value
        self.label = label
        return self


class IntValueSelector(int, Enum):
    def __new__(cls, value, selector):
        self = int.__new__(cls, value)
        self._value_ = value
        self.selector = selector
        return self
