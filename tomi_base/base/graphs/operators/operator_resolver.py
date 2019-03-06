from abc import ABC, abstractmethod

from tomi_base.base.graphs.operators import xor_categories, GraphOperation, direction_from_val


class OperatorsResolver(ABC):
    # +     __add__(self, other)        Addition
    # *     __mul__(self, other)        Multiplication
    # -     __sub__(self, other)        Subtraction
    # %     __mod__(self, other)        Remainder
    # /     __truediv__(self, other)    Division
    # <     __lt__(self, other)         Less than
    # <=    __le__(self, other)         Less than or equal to
    # ==    __eq__(self, other) 	    Equal to
    # !=    __ne__(self, other) 	    Not equal to
    # >     __gt__(self, other) 	    Greater than
    # >=    __ge__(self, other)         Greater than or equal to
    # +=    __iadd(self, other)         Addition assignment operator

    def __sub__(self, other):
        return self.operation_resolution(other,
                                         GraphOperation.LINK,
                                         direction_from_val(xor_categories(self.category, other.category)))

    def __gt__(self, other):
        return self.operation_resolution(other,
                                         GraphOperation.LINK_LEFT_RIGHT,
                                         direction_from_val(xor_categories(self.category, other.category)))

    def __lt__(self, other):
        return self.operation_resolution(other,
                                         GraphOperation.LINK_RIGHT_LEFT,
                                         direction_from_val(xor_categories(self.category, other.category)))

    def __add__(self, other):
        return self.operation_resolution(other,
                                         GraphOperation.ADD,
                                         direction_from_val(xor_categories(self.category, other.category)))

    # def __iadd__(self, other):
    #     return self.operation_resolution(other,
    #                                      GraphOperation.ASSIGN_ADD,
    #                                      direction_from_val(xor_categories(self.category, other.category)))
    #
    #
    # def __isub__(self, other):
    #     return self.operation_resolution(other,
    #                                      GraphOperation.ASSIGN_SUB,
    #                                      direction_from_val(xor_categories(self.category, other.category)))

    @abstractmethod
    def operation_resolution(self, other, operation, direction):
        raise NotImplementedError
