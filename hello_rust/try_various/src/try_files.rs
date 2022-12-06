use std::collections::HashMap;
use std::fs;
use std::fs::File;
use std::io;
use std::io::BufRead;
use std::io::BufReader;

pub fn try_all() {
    try_open_file();
    try_read_cargo_file();
}

fn try_open_file() {
    println!("Start try_open_file");

    let file_name = "Does not exist!";
    let a = File::open(file_name);
    println!("a = {:?}", a);

    if let Ok(file) = File::open(file_name) {
        println!("Was able to open the file: '{}'", file_name);
        drop(file);
    } else {
        println!("Was not able to open the file: '{}'", file_name);
        if let Err(err) = a {
            println!("Msg: {}", err.to_string());
        }
    }

    {
        let file_name = "Cargo.toml";
        if let Ok(file) = File::open(file_name) {
            let mut buff_reader = BufReader::new(file);
            loop {
                let mut buff = String::new();
                let result = buff_reader.read_line(&mut buff);
                if let Ok(res) = result {
                    if res == 0 {
                        break;
                    }
                    println!("{}", buff);
                } else {
                    println!("A error while reading the file: '{}'", file_name);
                    if let Some(err) = result.err() {
                        println!("Msg: {}", err.to_string());
                    }
                    break;
                }
            }
        }
    }

    println!("End try_open_file");
}

struct CargoFile {
    filename: String,
    loaded: bool,
    content: String,
    main_fields: HashMap<String, String>,
}

fn to_fields(line: String) -> Option<[String; 2]> {
    let fields: Vec<String> = line.split(" = ").map(|s| s.to_string()).collect();
    if fields.len() == 2 {
        let name = fields[0].clone();
        let value = String::from(fields[1].trim_matches('"'));
        let result: [String; 2] = [name, value];
        return Some(result);
    }
    return None;
}

impl CargoFile {
    fn new(filename: String) -> CargoFile {
        CargoFile {
            filename,
            loaded: false,
            content: String::new(),
            main_fields: HashMap::new(),
        }
    }

    fn to_map(&mut self) {
        let lines: Vec<String> = self.content.split("\n").map(|s| s.to_string()).collect();
        for line in lines {
            match to_fields(line) {
                Some(fields) => {
                    self.main_fields
                        .insert(fields[0].clone(), fields[1].clone());
                }
                None => continue,
            }
        }
    }

    fn read(&mut self) -> Result<(), io::Error> {
        self.content = fs::read_to_string(self.filename.as_str())?;
        self.to_map();
        self.loaded = true;
        Ok(())
    }

    fn get_name(&self) -> Result<String, &str> {
        if self.loaded {
            let lines: Vec<String> = self.content.split("\n").map(|s| s.to_string()).collect();
            for line in lines {
                let fields: Vec<&str> = line.split(" = ").collect();
                if fields.len() == 2 {
                    if fields[0] == "name" {
                        let result = String::from(fields[1].trim_matches('"'));
                        return Ok(result);
                    }
                }
            }
        }
        return Err("Unable to get the name");
    }

    fn get_field(&self, field_name: String) -> Result<String, String> {
        if self.loaded {
            let lines: Vec<String> = self.content.split("\n").map(|s| s.to_string()).collect();
            for line in lines {
                match to_fields(line) {
                    Some(fields) => {
                        if fields[0] == field_name {
                            return Ok(fields[1].clone());
                        }
                    }
                    None => continue,
                }
            }
        }
        let msg = format!("Unable to get the field: {}", field_name);
        return Err(msg);
    }
}

fn try_read_cargo_file() {
    println!("Start try_read_cargo_file");

    let mut my_cargo_file = CargoFile::new(String::from("Cargo.toml"));

    match my_cargo_file.read() {
        Ok(_) => (),
        Err(err) => {
            println!(
                "A error while reading the file: '{}'",
                my_cargo_file.filename
            );
            println!("Msg: {}", err.to_string());
        }
    }

    match my_cargo_file.get_name() {
        Ok(name) => println!("The name is: {}", name),
        Err(err) => println!("{}", err.to_string()),
    }

    match my_cargo_file.get_field(String::from("version")) {
        Ok(value) => println!("The version is: {}", value),
        Err(err) => println!("{}", err.to_string()),
    }

    match my_cargo_file.main_fields.get(&String::from("edition")) {
        Some(value) => println!("The edition is: {}", value),
        None => println!("the field edition is not found"),
    }

    println!("The main fields are: {:?}", my_cargo_file.main_fields);

    println!("End try_read_cargo_file");
}

#[allow(dead_code)]
fn try_template() {
    println!("Start try_template");

    println!("End try_template");
}
