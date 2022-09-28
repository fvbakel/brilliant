from dataclasses import dataclass
import logging
import graphviz

class Node: pass
class Position: pass

class Edge:

    def __init__(self,parent:Node,child:Node):
        self.parent:Node = parent
        self.child:Node = child
        self.active =True

    def reset(self):
        self.active = True

    def enable(self):
        self.active = True
    
    def disable(self):
        self.active = False

class Node:

    def __init__(self,id,weight):
        self.id:str = id
        self.weight = weight
        self.child_edges:set[Edge] = set()
        self.parent_edges:set[Edge] = set()
        self.prev:Node = None
        self.dist = -1 # is for infinit
        self.visited = False

    def __repr__(self):
        return self.id
        
    def reset(self):
        self.prev = None
        self.dist = -1 # is for infinit
        self.visited = False

    def add_child_edge(self,node:Node):
        if self == node:
            print("ERROR: connect to self is not allowed")
            return

        if not self.has_child_node(node):
            edge = Edge(self,node)
            self.child_edges.add(edge)
            node.add_parent_edge(edge)
            return edge

    def add_parent_edge(self,edge):
        self.parent_edges.add(edge)

    def has_child_node(self,node):
        edge = self.get_edge_to_child(node)
        if edge != None:
            return True
        return False

    def get_edge_to_child(self,node):
        for edge in self.child_edges:
            if edge.child == node:
                return edge
        return None

    def visit_all(self):
        self.visited = True
        for edge in self.child_edges:
            if edge.active and not edge.child.visited:
                edge.child.visit_all()

@dataclass(frozen=True,eq=True)
class EdgePair:
    forward:Edge
    backward:Edge

    def enable(self):
        self.forward.enable()
        self.backward.enable()

    def disable(self):
        self.forward.disable()
        self.backward.disable()

class Graph:

    def __init__(self):
        self.nodes:dict[str,Node] = dict()
        self.edges:set[Edge] = set()
        self.edge_pairs:set[EdgePair] =set()
        self.make_edge_pairs = True
        self.first = None
        self.last = None

    def reset(self):
        for node in self.nodes.values():
            node.reset()
    
    def get_node(self,id:str) -> Node:
        if id in self.nodes:
            return self.nodes[id]
        else:
            return None

    def get_or_create(self,id:str,weight:int = 0):
        if id in self.nodes:
            return self.nodes[id]
        else:
            node = Node(id,weight)
            self.nodes[id] = node
            if self.first is None:
                self.first = node
            return node
    
    def create_edge(self,parent:Node,child:Node):
        if parent == None or child == None:
            return

        edge = parent.add_child_edge(child)
        if edge != None:
            self.edges.add(edge)

            if self.make_edge_pairs:
                reverse_edge = child.get_edge_to_child(parent)
                if reverse_edge == None:
                    self.create_edge(child,parent)
                else:
                    pair = EdgePair(edge,reverse_edge) 
                    self.edge_pairs.add(pair)

    def is_fully_connected(self):
        self.reset()
        current = self.first
        current.visit_all()

        for node in self.nodes.values():
            if not node.visited:
                logging.debug(f"Node {node} is not connected")
                return False
        
        return True

    def check_recursion_first(self):
        return self.check_recursion(self.first)

    def check_recursion(self,node:Node):
        path = [node]
        is_recursive = self._check_recursion_internal(None,node,path)
        if is_recursive:
            logging.debug("Recursion found in path: {}".format(' -> '.join(map(str,path))))
        return is_recursive

    def _check_recursion_internal(self,previous_node:Node,current_node:Node,path:list[Node]):
        for edge in current_node.child_edges:
            if not edge.active or edge.child == previous_node:
                continue
            else:
                path.append(edge.child)
                if edge.child in set(path[:-1]):
                    return True
                if self._check_recursion_internal(current_node,edge.child,path):
                    return True
                path.pop()
        return False

    def get_min_node_not_visited(self):
        current = None
        for node in self.nodes.values():
            if node.visited == False:
                if current is None and node.dist != -1:
                    current = node
                else:
                    if node.dist != -1 and node.dist < current.dist:
                        current = node
        return current 

    def find_short_path_dijkstra(self,start:Node,end:Node):
        path:list[Node] = []
        self.reset()

        found = False
        
        start.dist = 0 
        current = start
        while current and not found:
            current.visited = True
            for edge in current.child_edges:
                if not edge.active:
                    continue
                other = edge.child
                if other.visited == False:
                    alt = current.dist + other.weight
                    if other.dist == -1 or alt < other.dist:
                        other.dist = alt
                        other.prev = current
            current = self.get_min_node_not_visited()
            if current == end:
                found = True
        
        if not found:
            print("Unable to find path from %s to %s" % (start.id, end.id))
        else:
            current = end
            while current is not None:
                path.insert(0,current)
                current = current.prev
        return path




# TODO Move below?
"""
class MatrixGraph??:

    # TODO: move logic below outside Graph
    def init_edges(self,allowed_directions = set(["r","d"])):
        row = 0
        while row  < self.size.nr_of_rows:
            col = 0
            while col < self.size.nr_of_cols:
                current = self.get(col,row)
                if current is None:
                    print("Error, can not find: ",MatrixGraph.make_label(col,row))
                else:
                    if "r" in allowed_directions and col != (self.size.nr_of_cols - 1):
                        child = self.get(col+1,row)
                        self.create_edge(direction='r',parent=current,child=child)
                    if "l" in allowed_directions and col != 0:
                        child = self.get(col-1,row)
                        self.create_edge(direction='l',parent=current,child=child)
                    if "d" in allowed_directions and row != (self.size.nr_of_rows - 1):
                        child = self.get(col,row +1)
                        self.create_edge(direction='d',parent=current,child=child)
                    if "u" in allowed_directions and row != 0:
                        child = self.get(col,row -1)
                        self.create_edge(direction='u',parent=current,child=child)
                col = col + 1
            row = row + 1

    def make_plain_graph(size:GridSize,allowed_directions = set(["r","d"])):
        graph = MatrixGraph()
        graph.size = size

        for row in range(0,graph.size.nr_of_rows):
            for col in range(0,graph.size.nr_of_cols):
                node = graph.get_or_create(col,row,1)

        graph.init_first_and_last()
        graph.init_edges(allowed_directions)

        return graph
   
    def read_from_file(filename,allowed_directions = set(["r","d"])):
        graph = MatrixGraph()
        line_nr = 0
        with open(filename) as fp:
            for line in fp:
                if line is not None:
                    line = line.strip()
                    fields = line.split(",")
                    if graph.size.nr_of_cols == 0:
                        graph.size.nr_of_cols = len(fields)
                    col = 0
                    
                    for field in fields:
                        if field != "-":
                            node = graph.get_or_create(line_nr,col,int(field))
                        col = col + 1
                    line_nr = line_nr + 1
        graph.nr_of_rows = line_nr
       
        graph.init_first_and_last()
        graph.init_edges(allowed_directions)

        return graph
"""

class Graph2Dot:

    def __init__(self,graph:Graph):
        self.graph = graph
        self._refresh()

    def _refresh(self):
        self.dot = graphviz.Digraph()
        self.dot.attr(rankdir='LR')
        for node in self.graph.nodes.values():
            self._add_node(node)
        for edge in self.graph.edges:
            #self._add_edge(edge)
            self._add_edge_as_node(edge)
        for pair in self.graph.edge_pairs:
            self._add_edge_pair(pair)

    def _add_node(self,node:Node):
        node_details = '<label> '
        node_details += node.id
        node_details += ' | <visited>'
        node_details += str(node.visited)
        self.dot.node(name=node.id,label=node_details,shape='record')
    
    def get_edge_id(edge):
        return f"{edge.parent.id} -> {edge.child.id}"

    def _add_edge_as_node(self,edge:Edge):
        id = Graph2Dot.get_edge_id(edge)
        node_details = '<parent> '
        node_details += edge.parent.id
        node_details += ' | <child> '
        node_details += edge.child.id
        node_details += ' | <active>'
        node_details += str(edge.active)
        self.dot.node(name=id,label=node_details,shape='record')

        self.dot.edge(edge.parent.id,id,headport='parent')
        self.dot.edge(id,edge.child.id,headport='child')

    def _add_edge_pair(self,pair:EdgePair):
        forward = Graph2Dot.get_edge_id(pair.forward)
        backward = Graph2Dot.get_edge_id(pair.backward)
        self.dot.edge(forward,backward,style="dotted")

    def _add_edge(self,edge:Edge):
        self.dot.edge(edge.parent.id,edge.child.id,label=str(edge.active))

    def render(self,filename:str,directory:str, format='svg'):
        self.dot.render(filename=filename,directory=directory, format=format)