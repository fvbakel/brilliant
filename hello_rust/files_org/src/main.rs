
pub mod module_one;
pub mod module_two;

mod my_main_module {
    pub fn a_func() {
        println!("Hello from my_main_module::a_func");
        a_module_only_function();
    }

    fn a_module_only_function() {
        println!("You can call me only inside  module my_main_module");
    }
}

fn main() {
    println!("Hello, world!");
    module_one::sub_module_one::say_hi();
    my_main_module::a_func();
    module_two::sub_mod_in_two::fun_in_sub_mod_two();
}
