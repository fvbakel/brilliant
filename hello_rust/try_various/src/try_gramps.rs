use std::collections::HashMap;
use std::fs::File;
use std::io::BufRead;
use std::io::BufReader;

pub fn try_gramps() {
    let filename = String::from("/home/fvbakel/stamboom/exports/stamboom-2022-04-12.csv");
    let data = GrampsData::get_from_file(&filename);
    println!("Places={:?}", data.places.keys());
    println!("Persons={:?}", data.persons.keys());
}

#[derive(Debug,Clone)]
// Place,Title,Name,Type,Latitude,Longitude,Code,Enclosed_by,Date
struct Place {
    id: String,
    name: String,
}

#[derive(Debug)]
// Person,Surname,Given,Call,Suffix,Prefix,Title,Gender,Birth date,Birth place,Birth source,Baptism date,Baptism place,Baptism source,Death date,Death place,Death source,Burial date,Burial place,Burial source,Note
struct Person {
    id: String,
    surname: String,
    given: String,
    birth_place: Option<Place>,
}

struct GrampsData {
    places: HashMap<String, Place>,
    persons: HashMap<String, Person>,
}

enum ReadMode {
    Search,
    ReadPlace,
    ReadPerson,
}

impl GrampsData {
    fn new() -> GrampsData {
        GrampsData {
            places: HashMap::new(),
            persons: HashMap::new(),
        }
    }

    fn get_from_file(filename: &String) -> GrampsData {
        fn parse_search(fields: &Vec<&str>) -> ReadMode {
            match fields[0] {
                "Place" => {
                    return ReadMode::ReadPlace;
                }
                "Person" => {
                    return ReadMode::ReadPerson;
                }
                _ => return ReadMode::Search,
            }
        }

        // Person,Surname,Given,Call,Suffix,Prefix,Title,Gender,Birth date,Birth place,Birth source,Baptism date,Baptism place,Baptism source,Death date,Death place,Death source,Burial date,Burial place,Burial source,Note
        fn parse_person(fields: &Vec<&str>, data: &mut GrampsData) -> ReadMode {
            match fields.len() {
                i if i > 9 => {
                    let place_name = String::from(fields[8]).replace("[","").replace("]","");
                    let place = data.places.get(&place_name).cloned();
                    // TODO: How to replace the relation with place to a pointer?
                    
                    let person = Person {
                        id: String::from(fields[0]).replace("[","").replace("]",""),
                        surname: String::from(fields[1]),
                        given: String::from(fields[2]),
                        birth_place: place,
                    };
                    data.persons.insert(person.id.clone(), person);
                    return ReadMode::ReadPerson;
                }
                1 => return ReadMode::Search,
                _ => return ReadMode::ReadPerson,
            }
        }

        // Place,Title,Name,Type,Latitude,Longitude,Code,Enclosed_by,Date
        fn parse_place(fields: &Vec<&str>, data: &mut GrampsData) -> ReadMode {
            match fields.len() {
                i if i > 2 => {
                    let place = Place {
                        id: String::from(fields[0]).replace("[","").replace("]",""),
                        name: String::from(fields[2]),
                    };
                    data.places.insert(place.id.clone(), place);
                    return ReadMode::ReadPlace;
                }
                1 => return ReadMode::Search,
                _ => return ReadMode::ReadPlace,
            }
        }

        fn read_file(filename: &String) -> std::io::Result<GrampsData> {
            let mut data = GrampsData::new();
            let f = File::open(filename)?;
            let mut reader = BufReader::new(f);
            let mut buff = String::new();
            let mut mode: ReadMode = ReadMode::Search;
            loop {
                let result = reader.read_line(&mut buff).unwrap();
                if result == 0 {
                    break;
                }
                let cleaned = buff.replace(", ", "; ");
                let fields: Vec<&str> = cleaned.split(",").collect();
                mode = match mode {
                    ReadMode::Search => parse_search(&fields),
                    ReadMode::ReadPerson => parse_person(&fields, &mut data),
                    ReadMode::ReadPlace => parse_place(&fields, &mut data),
                };
                buff.clear();
            }
            Ok(data)
        }
        read_file(&filename).unwrap()
    }
}
