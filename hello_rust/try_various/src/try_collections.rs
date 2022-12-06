use std::collections::HashMap;

pub fn try_all() {
    try_vector_one();
    try_string();
    try_slices_of_string();
    try_slices_of_array();
    try_string_utf8();
    try_hash_maps();
    try_string_splitters();
}

fn try_vector_one() {
    let mut v_1: Vec<i32> = Vec::new();
    let v_2 = vec![1, 2, 3];
    v_1.push(1);
    let o = v_2.get(1);
    let o_1 = if let Some(x) = o { *x } else { i32::from(0) };
    v_1.push(o_1);

    println!("v1 has size {}", v_1.len());
}

fn try_string() {
    let mut s_1 = String::from("The value of string s_1");
    let s_2 = " and this is s_2";
    s_1.push_str(s_2);
    println!("The value of s_1 is {}", s_1);
    println!("The value of s_2 is {}", s_2);

    let s_3 = String::from("Hello, ");
    let s_4 = String::from("world!");
    let s_5 = s_3 + &s_4;
    println!("The value of s_5 is {}", s_5);
    // below is not possible because s_3 is moved!
    // println!("The value of s_4 is {}",s_4);
    println!("The value of s_4 is {}", s_4);
}

fn try_string_utf8() {
    println!("Start try_string_utf8.");

    let hello = "Здравствуйте";
    println!("Hello: [{hello}]");
    let len = hello.len();
    println!("Nr of bytes (len): {len}");
    let nr_chars = hello.chars().count();
    println!("Nr of chars: {nr_chars}");

    println!("In char values:");
    for char in hello.chars() {
        print!("{char},");
    }
    println!();

    println!("In byte values:");
    for byte in hello.as_bytes() {
        print!("{:#02X?} ,", byte);
    }
    println!();

    println!("In char byte values:");
    for char in hello.chars() {
        let mut buffer = [0; 4];
        let bytes = char.encode_utf8(&mut buffer);
        print!("{char}= ");
        for byte in bytes.as_bytes() {
            print!("{:#02X?} ,", byte);
        }
        print!(" char size: {}", std::mem::size_of_val(&char));
        print!(" bytes len: {}", bytes.len());
        print!(" char.len_utf8(): {}", char.len_utf8());

        println!();
    }

    println!("{:#02X?}", hello.as_bytes());

    println!("End try_string_utf8.");
}

fn try_slices_of_string() {
    println!("Start try_slices_of_string.");
    let my_string = String::from("hello world");

    // `first_word` works on slices of `String`s, whether partial or whole
    let word = first_word(&my_string[0..6]);
    println!("The value of word is {}", word);
    let word = first_word(&my_string[..]);
    println!("The value of word is {}", word);
    // `first_word` also works on references to `String`s, which are equivalent
    // to whole slices of `String`s
    let word = first_word(&my_string);
    println!("The value of word is {}", word);

    let my_string_literal = "hello world";

    // `first_word` works on slices of string literals, whether partial or whole
    let word = first_word(&my_string_literal[0..6]);
    println!("The value of word is {}", word);
    let word = first_word(&my_string_literal[..]);
    println!("The value of word is {}", word);

    // Because string literals *are* string slices already,
    // this works too, without the slice syntax!
    let word = first_word(my_string_literal);
    println!("The value of word is {}", word);
    println!("End try_slices_of_string.");
}

fn first_word(s: &str) -> &str {
    let bytes = s.as_bytes();

    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }

    &s[..]
}

fn try_slices_of_array() {
    let a = [1, 2, 3, 4, 5];
    println!("Given array:");
    for val in a {
        print!("{val},");
    }

    println!("\nSlice [1..3]:");
    let slice = &a[1..3];
    for val in slice {
        print!("{val},");
    }

    println!("\nSlice [..3]:");
    let slice = &a[..3];
    for val in slice {
        print!("{val},");
    }

    println!("\nSlice [2..]:");
    let slice = &a[2..];
    for val in slice {
        print!("{val},");
    }

    println!("\nSlice [2..-2]:");
    let slice = &a[2..];
    for val in slice {
        print!("{val},");
    }
}

fn try_hash_maps() {
    println!("Start try_hash_maps.");
    {
        let mut scores = HashMap::new();

        scores.insert(String::from("White"), 5);
        scores.insert(String::from("Blue"), 10);
        scores.insert(String::from("Yellow"), 50);
        // does change the value of Blue
        scores.insert(String::from("Blue"), 15);
        // does not change the value of Blue
        scores.entry(String::from("Blue")).or_insert(60);
        // makes a new entry
        scores.entry(String::from("LightBlue")).or_insert(55);

        // add one
        let score = scores.entry(String::from("LightBlue")).or_insert(0);
        *score += 1;

        scores
            .entry(String::from("LightBlue"))
            .and_modify(|e| *e += 1);

        scores
            .entry(String::from("Does not exist"))
            .and_modify(|e| *e += 1);

        let key = String::from("Green");
        let value = 25;
        scores.insert(key, value);
        // below is not possible
        //println!("Key={}",key);
        // below is possible because value is int
        println!("value={}", value);

        let key = String::from("Pink");
        let value = 35;
        scores.insert(key.clone(), value);
        println!("Key={}", key);

        let team_name = String::from("Blue");
        let score = scores.get(&team_name);
        let score = if let Some(x) = score {
            *x
        } else {
            i32::from(0)
        };
        println!("score for team [{0}] =[{1}]", team_name, score);

        let team_name = String::from("Blue");
        let score = scores.get(&team_name).copied().unwrap_or(0);
        println!("score for team [{0}] =[{1}]", team_name, score);

        let team_name = String::from("Does not exist");
        let score = scores.get(&team_name).copied().unwrap_or(0);
        println!("score for team [{0}] =[{1}]", team_name, score);

        println!("HashMap scores={:?}", scores);

        println!("Key values:");
        for (key, value) in &scores {
            println!("{:10}: {}", key, value);
        }
    }

    // Part Two
    {
        println!("Part Two start");
        let mut map = HashMap::new();
        let s = String::from("A|B|C|A|B|E|Q");
        for field in s.split('|') {
            map.entry(String::from(field))
                .and_modify(|e| *e += 1)
                .or_insert(1);
        }
        println!("Count of {0} results: {1:?}", s, map);
    }
    println!("End try_hash_maps.");
}

fn try_string_splitters() {
    println!("Start try_string_splitters.");
    let s = String::from("  A one|  B two | C three ");

    println!("s.split('|')");
    let fields = s.split('|');
    println!("Fields={:?}", fields);

    println!("s.split('|').collect()");
    let fields: Vec<&str> = s.split('|').collect();
    println!("Fields={:?}", fields);

    println!("s.split(\"Q\").collect()");
    let fields: Vec<&str> = s.split("Q").collect();
    println!("Fields={:?}", fields);

    println!("s.split(' ').collect()");
    let fields: Vec<&str> = s.split(' ').collect();
    println!("Fields={:?}", fields);

    println!("s.split(' ').collect()");
    let fields: Vec<&str> = s.split_whitespace().collect();
    println!("Fields={:?}", fields);

    println!("End try_string_splitters.");
}

#[allow(dead_code)]
fn try_template() {
    println!("Start try_template");

    println!("End try_template");
}
