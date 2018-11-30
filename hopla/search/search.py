from ujson import dumps

from objectpath import Tree

from hopla.documents.document import Document


class Search(object):
    @staticmethod
    def children_documents(document):
        tree = Tree(document.toDict())
        return [Document.from_str(dumps(d["__object"])) for d in
                list(tree.execute('$..*[@.__type is "BaseDocument" and @.__object]'))]
