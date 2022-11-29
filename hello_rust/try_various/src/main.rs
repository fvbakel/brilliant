use std::collections::HashSet;


mod try_collections;
mod try_files;
/*
struct Node {
    children: ve
}

*/

#[derive(Debug)]
#[allow(dead_code)]
struct AObject {
    id: String
}

impl AObject {

    fn print(&self) {
        println!("A object {:?}",self);
    }
}


struct Person<'a> {
    id: String,
    some_rel: &'a AObject
}

impl <'q> Person<'q> {

    fn print(&self) {
        println!("Person id: {}",self.id);
        self.some_rel.print();
    }
}

impl <'a> Person<'a> {

    fn print_two(&self) {
        println!("By TWO Person id: {}",self.id);
        self.some_rel.print();
    }
}

fn plus_one(x: i32) -> i32 {
    x + 1
}

#[allow(unused_assignments)]
fn plus_one_ref(mut x: i32)  {
    // changes to x to not affect the original input parameter!
    x = x + 1;
}

fn plus_one_ref_two(x:&mut i32)  {
    *x = *x + 1;
}

fn plus_one_option(x: Option<i32>) -> Option<i32> {
    match x {
        None => None,
        Some(i) => Some(i + 1),
    }
}

fn get_print_value(x: Option<i32>) -> String {
    match x {
        None => String::from("None"),
        Some(i) => i.to_string(),
    }
}

fn print_value(x: Option<i32>) {
    if let Some(y) = x {
        println!("The value is {}",y);
    }
}

fn try_out_plus_one(){
    println!("Start try_out_plus_one...");
    let c: i32 = 6;
    let mut d:i32 = 8;
    let mut a: i32 = 5;
    let e = plus_one_option(Some(22));
    let f = plus_one_option(None);

    let b: i32 = plus_one(a);

    a = plus_one(2);
    a = plus_one(a);
    //value of c does NOT change!
    plus_one_ref(c);
    // value of d does change!
    plus_one_ref_two(&mut d);

    println!("The value of a is: {a}");
    println!("The value of b is: {b}");
    println!("The value of c is: {c}");
    println!("The value of d is: {d}");
    println!("The value of e is: {}",get_print_value(e));
    print_value(e);
    println!("The value of f is: {}",get_print_value(f));
    print_value(f);
}

fn try_out_person_rel() {
    println!("Start try_out_Person_rel...");
    let o_1: AObject = AObject { id: String::from("002") };
    let p_2: Person = Person { id: String::from("P-002"), some_rel: &o_1 };
    p_2.print();
    o_1.print();
    p_2.print_two();
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


#[allow(dead_code)]
enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter,
}


impl Coin {
    fn value_in_cents(&self) -> u8 {
        match self {
            Coin::Penny => 1,
            Coin::Nickel => 5,
            Coin::Dime => 10,
            Coin::Quarter => 25,
        }
    }
}

fn try_out_enum_basics() {
    println!("whats up with enums and coins?");

    let p = Coin::Dime;
    println!("The value of a Dime is {}",p.value_in_cents());

    let p = Coin::Penny;
    println!("The value of a Penny is {}",p.value_in_cents());

}

fn main() {
    println!("Just trying to make a graph in Rust...");
    try_out_set();

    try_out_struct_1();

    try_out_person_rel();

    try_out_plus_one();

    try_out_enum_basics();

    crate::try_collections::try_all();
    crate::try_files::try_all();
    
}
