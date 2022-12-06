use std::cell::RefCell;
use std::rc::Rc;

#[allow(dead_code)]
fn try_template() {
    println!("Start try_template");

    println!("End try_template");
}

#[derive(Debug)]
struct Node {
    value: i32,
    children: RefCell<Vec<Rc<Node>>>,
}


pub fn try_main() {
    println!("Start try_main");
    let leaf = Rc::new(Node {
        value: 3,
        children: RefCell::new(vec![]),
    });

    let branch = Rc::new(Node {
        value: 5,
        children: RefCell::new(vec![Rc::clone(&leaf)]),
    });

    println!("End try_main");
}
