

class Edge:

    def __init__(self,parent,child):
        self.parent = parent
        self.child = child
    
class Node:

    def __init__(self,x,y,weight):
        self.x = x
        self.y = y
        self.label = MatrixGraph.make_label(x,y)
        self.weight = weight
        self.child_edges = set()
        self.parent_edges = set()
        self.prev = None
        self.dist = -1 # is for infinit
        self.visited = False

    def __repr__(self):
        return self.label
        
    def reset(self):
        self.prev = None
        self.dist = -1 # is for infinit
        self.visited = False

    def add_child_edge(self,node):
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
        for edge in self.child_edges:
            if edge.child == node:
                return True

        return False

class MatrixGraph:

    def __init__(self):
        self.nodes = dict()
        self.edges = set()
        self._first = None
        self.col_first = None
        self.col_last = None
        self.nr_of_rows = 0
        self.nr_of_cols = 0

    def reset(self):
        for node in self.nodes.values():
            node.reset()
    
    def get(self,x,y):
        label = MatrixGraph.make_label(x,y)
        if label in self.nodes:
            return self.nodes[label]
        else:
            return None

    def get_or_create(self,x,y,weight):
        label = MatrixGraph.make_label(x,y)
        if label in self.nodes:
            return self.nodes[label]
        else:
            node = Node(x,y,weight)
            self.nodes[label] = node
            if self._first is None:
                self._first = node
            return node
    
    def init_first_and_last(self):
        self.col_first = self.get_or_create("col",0,0)
        self.col_last = self.get_or_create("col",(self.nr_of_cols-1),0)
    
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

    def sum_path_l_r(self):
        total = 0
        start = self.get(0,0)
        end = self.get((self.nr_of_rows -1),(self.nr_of_cols -1))
        path = self.find_short_path_dijkstra(start,end)

        for node in path:
            total = total + node.weight
        print(path)
        print("Sum is:", total)
    
    def sum_path_l_r_col(self):
        total = 0
        start = self.col_first
        end = self.col_last
        path = self.find_short_path_dijkstra(start,end)

        for node in path:
            total = total + node.weight
        print(path)
        print("Sum is:", total)

    def find_short_path_dijkstra(self,start,end):
        path = []
        self.reset()

        found = False
        
        start.dist = 0 
        current = start
        while current and not found:
            current.visited = True
            for edge in current.child_edges:
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
            print("Unable to find path from %s to %s" % (start.label, end.label))
        else:
            current = end
            while current is not None:
                path.insert(0,current)
                current = current.prev
        return path

    def make_label(x,y):
        return str(x) + "-" + str(y)

    def init_edges(self,allowed_directions = set(["r","d"])):
        row = 0
        while row  < self.nr_of_rows:
            col = 0
            while col < self.nr_of_cols:
                current = self.get(row,col)
                if current is None:
                    print("Error, can not find: ",MatrixGraph.make_label(row,col))
                else:
                    if "r" in allowed_directions and col != (self.nr_of_cols - 1):
                        child = self.get(row,col+1)
                        if child is not None:
                            edge = current.add_child_edge(child)
                            self.edges.add(edge)
                        else:
                            print("Error, can not find child in next col for: ",current.label)
                    if "l" in allowed_directions and col != 0:
                        child = self.get(row,col-1)
                        if child is not None:
                            edge = current.add_child_edge(child)
                            self.edges.add(edge)
                        else:
                            print("Error, can not find child in previous col for: ",current.label)
                    if "d" in allowed_directions and row != (self.nr_of_rows - 1):
                        child = self.get(row +1,col)
                        if child is not None:
                            edge = current.add_child_edge(child)
                            self.edges.add(edge)
                        else:
                            print("Error, can not find child in next row for: ",current.label)    
                    if "u" in allowed_directions and row != 0:
                        child = self.get(row -1,col)
                        if child is not None:
                            edge = current.add_child_edge(child)
                            self.edges.add(edge)
                        else:
                            print("Error, can not find child in previous row for: ",current.label)    
                    if col == 0:
                        edge = self.col_first.add_child_edge(current)
                        self.edges.add(edge)
                    if col == (self.nr_of_cols - 1):
                        edge = current.add_child_edge(self.col_last)
                        self.edges.add(edge)

                col = col + 1
            row = row + 1

    def make_plain_graph(nr_of_cols = 4,nr_of_rows = 4,allowed_directions = set(["r","d"])):
        graph = MatrixGraph()
        graph.nr_of_cols = nr_of_cols
        graph.nr_of_rows = nr_of_rows

        for row in range(0,graph.nr_of_rows):
            for col in range(0,graph.nr_of_cols):
                node = graph.get_or_create(row,col,1)

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
                    if graph.nr_of_cols == 0:
                        graph.nr_of_cols = len(fields)
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



if __name__ == "__main__":
    #graph = MatrixGraph.read_from_file("./data/p081_small_matrix.txt",set(["r","u","d","l"]))
    #graph = MatrixGraph.read_from_file("./data/p083_matrix.txt",set(["r","u","d","l"]))
    #graph = MatrixGraph.read_from_file("./data/p082_matrix.txt",set(["r","u","d"]))
    #graph = MatrixGraph.read_from_file("./data/p081_matrix.txt")
    #graph.sum_path_l_r_col()
    graph = MatrixGraph.make_plain_graph(4,4,set(["r","d"]))
    graph.sum_path_l_r()
