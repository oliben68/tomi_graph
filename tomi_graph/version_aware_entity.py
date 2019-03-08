import warnings
from abc import ABC, abstractmethod
from datetime import datetime

from tomi_graph.frozen_entity_warning import FrozenEntityWarning


class VersionAwareEntity(ABC):
    @property
    def frozen(self):
        if not hasattr(self, "_frozen"):
            object.__setattr__(self, "_frozen", False)
        return getattr(self, "_frozen", False)

    @abstractmethod
    def clone(self, new=None):
        raise NotImplementedError

    def __setattr__(self, name, value):
        if name == "_frozen":
            return
        try:
            if getattr(self, "_frozen", False):
                warnings.warn("frozen", FrozenEntityWarning)
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
                setattr(self, "_version", int(getattr(self, "_version", 0)))
            except ValueError:
                setattr(self, "_version", 0)
            clone._version = getattr(self, "_version", 0) + 1
        self.freeze()

        if data is not None:
            clone.set_data(data)
        clone._update_date = timestamp

        return clone
