from abc import ABC, abstractmethod


class BaseValidator(ABC):
    @abstractmethod
    def __init__(self, validation_expression):
        raise NotImplementedError

    @abstractmethod
    def validate(self, entity):
        raise NotImplementedError
