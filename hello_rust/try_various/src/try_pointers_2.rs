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


fn print_node(node: &Node,level: usize) {
    let indent = level * 3;
    println!("{:3}: {:indent$} Node: {}",level,"",node.value);
    for child in node.children.borrow().iter() {
        print_node(child, level  + 1 );
    }

}

fn new_node(value:i32) -> Rc<Node> {
    Rc::new(Node {
        value: value,
        children: RefCell::new(vec![]),
    })
}

fn add_child(parent: Rc<Node>, child:Rc<Node>) {
    parent.children.borrow_mut().push(Rc::clone(&child));
}

fn remove_child(parent: Rc<Node>, index: usize) {
    parent.children.borrow_mut().swap_remove(index);
}

fn make_structure() -> Rc<Node> {
    let top = new_node(0);
    let leaf1 = new_node(1);
    let leaf2 = new_node(2);
    add_child(Rc::clone(&top),Rc::clone(&leaf1));
    add_child(Rc::clone(&top),Rc::clone(&leaf2));
    top
}

pub fn try_main() {
    println!("Start try_main");
    let leaf = Rc::new(Node {
        value: 1,
        children: RefCell::new(vec![]),
    });

    let leaf2 = Rc::new(Node {
        value: 2,
        children: RefCell::new(vec![]),
    });

    let leaf3 = new_node(3);

    let branch = Rc::new(Node {
        value: 10,
        children: RefCell::new(vec![Rc::clone(&leaf)]),
    });

    branch.children.borrow_mut().push(Rc::clone(&leaf2));
    branch.children.borrow_mut().push(Rc::clone(&leaf3));

    let leaf4 = new_node(4);
    add_child(Rc::clone(&branch),Rc::clone(&leaf4));

    print_node(&branch,0);

    println!("Structure 2:");
    let test_s = make_structure();
    print_node(&test_s,0);

    // it is not possible to modify the node!
    //leaf.value = 9;

    remove_child(Rc::clone(&test_s),1);

    println!("Structure 2 after remove:");
    print_node(&test_s,0);
    

    println!("End try_main");
}
