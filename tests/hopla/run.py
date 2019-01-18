from hopla.entities.entity import Entity
from hopla.graphs.graph import Graph

b_doc = Entity("B", core_id="B")
c_doc = Entity("C", core_id="C")
a_doc = Entity(b_doc, c_doc, core_id="A")
sub_doc = Entity(a_doc, core_id="SUB_ID")
root = Entity(sub_doc, {"D": Entity("D")}, core_id="ROOT")

self = Graph(root)

self.assemble()
