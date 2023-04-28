mod example_1;
mod example_2;
mod my_example;
mod petgraph_1;


fn main() {
    println!("Hello, graphviz");
    crate::example_1::main();
    crate::example_2::main();
    crate::my_example::main();
    crate::petgraph_1::run_all();
}
