from hopla.graphs.category import Category


class Core(object):
    category = Category._CORE
    _workspace = None

    @property
    def workspace(self):
        if self._workspace is None:
            from hopla.workspace import WORKSPACE
            self._workspace = WORKSPACE
        return self._workspace
