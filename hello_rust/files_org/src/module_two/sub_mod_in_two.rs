use crate::module_one::sub_module_one as a;

pub fn fun_in_sub_mod_two() {
    println!("Hi from fun_in_sub_mod_two");
    //crate::module_one::sub_module_one::say_hi()
    a::say_hi();
}