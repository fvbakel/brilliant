extern crate petgraph;
use petgraph::graph::Graph;
use petgraph::dot::Dot;
use petgraph::algo;

use std::fs::File;
use std::io::Write;


pub fn run_all() {
    example_1();
    example_2();
    example_3();
}

fn example_1() {
    let mut g : Graph<&str, &str> = Graph::new();
    let a = g.add_node("Node (vertex): a");
    let b = g.add_node("Node (vertex): b");
    g.add_edge(a, b, "edge from a → b");

    let mut f = File::create("petgraph_1.dot").unwrap();

    write!(&mut f, "{}",Dot::new(&g)).unwrap();

}

fn example_2() {
    let mut g : Graph<i32, i32> = Graph::new();
    let a = g.add_node(1);
    let b = g.add_node(2);
    let c = g.add_node(3);
    g.add_edge(a, b, 1);
    g.add_edge(a, c, 2);
    g.add_edge(b, c, 3);

    let mut f = File::create("petgraph_2.dot").unwrap();

    let dot = Dot::new(&g);
    
    write!(&mut f, "{}",dot).unwrap();
}

fn example_3() {
    let mut g : Graph<i32, i32,petgraph::Undirected> = Graph::new_undirected();
    let a = g.add_node(11);
    let b = g.add_node(12);
    let c = g.add_node(13);
    let d = g.add_node(14);
    g.add_edge(a, b, 1);
    g.add_edge(b, c, 1);
    g.add_edge(c, d, 1);
    g.add_edge(b, d, 1);

    let path = algo::dijkstra(&g,a,Some(d),|_| 1);
    println!("Dijkstra cost map from 11 to 14:\n{:?}",path);

    let path = algo::astar(
        &g, 
        a, 
        |n| n== d, 
        |e| *e.weight(), 
        |_| 0
    );
    println!("A start shortest path from 11 to 14 raw data:\n{:?}",&path);

    match path {
        Some((cost, path)) => {
            println!("The total cost is {}: {:?}", cost, path);
            for node in path {
                println!("The next node index {:?} value: {:?}",node,g.node_weight(node));
            }
        }
        None => println!("There was no path"),
    }

    println!("After match");

    let mut f = File::create("petgraph_3.dot").unwrap();
    let dot = Dot::new(&g);
    write!(&mut f, "{}",dot).unwrap();
}