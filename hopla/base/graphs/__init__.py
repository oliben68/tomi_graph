from datetime import datetime
import warnings
from abc import ABC, abstractmethod
from enum import Enum

from hopla.base.graphs.frozen_object_warning import FrozenObjectWarning


class Category(Enum):
    NONE = 0
    _CORE = 1
    NODE = 2
    RELATIONSHIP = 4
    INDEX = 8
    GRAPH = 16


class BaseGraphEntity(ABC):
    category = Category._CORE

    @abstractmethod
    def to_graph(self):
        raise NotImplementedError


class VersionAware(ABC):
    @property
    def frozen(self):
        if not hasattr(self, "_frozen"):
            object.__setattr__(self, "_frozen", False)
        return self._frozen

    @abstractmethod
    def clone(self, new=None):
        raise NotImplementedError

    def __setattr__(self, name, value):
        if name == "_frozen":
            return
        try:
            if self._frozen:
                warnings.warn("frozen", FrozenObjectWarning)
                return
        except AttributeError:
            object.__setattr__(self, "_frozen", False)

        object.__setattr__(self, name, value)

    def freeze(self):
        object.__setattr__(self, "_frozen", True)

    def unfreeze(self):
        object.__setattr__(self, "_frozen", False)

    def new_version(self, data=None):
        timestamp = int(datetime.utcnow().timestamp())
        clone = self.clone()
        try:
            clone._version += 1
        except TypeError:
            try:
                self._version = int(self._version)
            except ValueError:
                setattr(self, "_version", 0)
            clone._version = self._version + 1
        self.freeze()

        if data is not None:
            clone.set_data(data)
        clone._update_date = timestamp

        return clone
