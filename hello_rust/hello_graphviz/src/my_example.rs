use std::cell::RefCell;
use std::fs::File;

#[derive(Clone)]
struct Node {
    id: String
}

#[derive(Clone)]
struct Edge<'a> {
    from: RefCell<&'a Node>,
    to: RefCell<&'a Node>
}

struct Graph<'a> {
    nodes: Vec<Node>,
    edges: Vec<Edge<'a>>
}

fn make_graph<'a>(nodes:Vec<Node>) -> Graph<'a> {

    let g:Graph<'a> = Graph {
        nodes: nodes,
        edges: Vec::new()
    };

/*     let edge_1:Edge = Edge {
        from: RefCell::new(&node),
        to: RefCell::new(&g.nodes[1]),
    };
    g.edges.push(edge_1);
*/
    g
}

impl<'a> dot::Labeller<'a, Node, Edge<'a>> for Graph<'a> {
    fn graph_id(&'a self) -> dot::Id<'a> { 
        dot::Id::new("myexample").unwrap() 
    }

    fn node_id(&'a self, n: &Node) -> dot::Id<'a> {
        dot::Id::new(n.id.clone()).unwrap()
    }
    
}

impl<'a> dot::GraphWalk<'a, Node, Edge<'a>> for Graph<'a> {
    fn nodes(&self) -> dot::Nodes<'a,Node> { 
        self.nodes.iter().cloned().collect() 
    }
    fn edges(&'a self) -> dot::Edges<'a,Edge<'a>> { 
        self.edges.iter().cloned().collect() 
    }

    fn source(&self, e: &Edge) -> Node {
         e.from.borrow().clone()
    }
    fn target(&self, e: &Edge) -> Node {
        e.to.borrow().clone()
   }
}

pub fn main() {
    
    let mut f = File::create("my_example.dot").unwrap();
    let mut nodes: Vec<Node> = Vec::new();
    for i in 0..5 {
        let node = Node {
            id: format!("Node{}",i)
        };
        nodes.push(node);
    }

    let g = make_graph(nodes);

    dot::render(&g, &mut f).unwrap()
}