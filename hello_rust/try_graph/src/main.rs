use std::collections::HashSet;
/*
struct Node {
    children: ve
}

*/

struct AObject {
    id: String
}

impl AObject {

    fn print(&self) {
        println!("A object id: {}",self.id);
    }
}

struct Person<'a> {
    id: String,
    some_rel: &'a AObject
}

impl <'a> Person<'a> {

    fn print(&self) {
        println!("Person id: {}",self.id);
        self.some_rel.print();
    }
}

fn try_out_person_rel() {
    println!("Start try_out_Person_rel...");
    let o_1: AObject = AObject { id: String::from("002") };
    let p_2: Person = Person { id: String::from("P-002"), some_rel: &o_1 };
    p_2.print();
    o_1.print();
}

fn try_out_struct_1() {
    let p_1: AObject = AObject {
        id: String::from("001")
    };

    p_1.print();
}

fn try_out_set() {
    let mut my_set : HashSet<i32> = HashSet::new();
    assert!(my_set.insert(1));

    // handling the return value is not required?
    my_set.insert(2);
    my_set.insert(2);
}

fn main() {
    println!("Just trying to make a graph in Rust...");
    try_out_set();

    try_out_struct_1();

    try_out_person_rel();
    
}
