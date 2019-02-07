from enum import Enum

from hopla.relationships.core import NULL_VAL


def reverse(n):
    return int('{:032b}'.format(n)[::-1], 2)


def xor_categories(s, o):
    return s.value ^ reverse(o.value)


class Category(Enum):
    NONE = 0
    _CORE = 1
    ENTITY = 2
    RELATIONSHIP = 4
    INDEX = 8
    GRAPH = 16


class GraphOperationDirection(Enum):
    # CategorySelf_CategoryOther = CategorySelf ^ reverse(CategoryOther)
    ENTITY_ENTITY = xor_categories(Category.ENTITY, Category.ENTITY)  # 1073741826
    ENTITY_RELATIONSHIP = xor_categories(Category.ENTITY, Category.RELATIONSHIP)  # 536870914
    RELATIONSHIP_RELATIONSHIP = xor_categories(Category.RELATIONSHIP, Category.RELATIONSHIP)  # 536870916
    RELATIONSHIP_ENTITY = xor_categories(Category.RELATIONSHIP, Category.ENTITY)  # 1073741828
    GRAPH_GRAPH = xor_categories(Category.GRAPH, Category.GRAPH)
    GRAPH_ENTITY = xor_categories(Category.GRAPH, Category.ENTITY)
    GRAPH_RELATIONSHIP = xor_categories(Category.GRAPH, Category.RELATIONSHIP)
    SELF_ASSIGNMENT = 0
    NOT_FOUND = None


class GraphOperation(Enum):
    ADD = dict(magic="__add__", operator="+")  # +     __add__(self, other)     Addition
    SUB = dict(magic="__sub__", operator="-")  # -     __sub__(self, other)     Subtraction
    LINK = dict(magic="__sub__", operator="+")  # -     __sub__(self, other)     Subtraction
    LINK_RIGHT_LEFT = dict(magic="__lt__", operator="<")  # <     __lt__(self, other)   Less than
    LINK_LEFT_RIGHT = dict(magic="__gt__", operator=">")  # >     __gt__(self, other)   Greater than
    ASSIGN_ADD = dict(magic="__iadd__", operator="+=")  # +=    __iadd(self, other)      Addition assignment operator
    ASSIGN_SUB = dict(magic="__isub__", operator="-=")  # -=    __isub__(self, other)    Addition assignment operator
    # *     __mul__(self, other)        Multiplication
    # %     __mod__(self, other)        Remainder
    # /     __truediv__(self, other)    Division
    # <=    __le__(self, other)         Less than or equal to
    # ==    __eq__(self, other) 	    Equal to
    # !=    __ne__(self, other) 	    Not equal to
    # >=    __ge__(self, other)         Greater than or equal to


def direction_from_val(value):
    found_value = [m for m in GraphOperationDirection.__members__.values() if m.value == value]
    if len(found_value) > 0:
        return found_value[0]
    return GraphOperationDirection.NOT_FOUND


class DefaultValues(Enum):
    ENTITY = dict(entity_type=None, core_id=None, encoding=None, key=None, name=None, data=None, ttl=-1)
    RELATIONSHIP = dict(name=None, rel_type=None, protection=None, data=None, on_gc_collect=NULL_VAL)
