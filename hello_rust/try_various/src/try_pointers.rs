use std::collections::HashMap;
use std::rc::Rc;

#[allow(dead_code)]
fn try_template() {
    println!("Start try_template");

    println!("End try_template");
}

pub fn try_all() {

    try_box();
    try_collection();

    

}

fn try_collection() {
    println!("Start try_collection");
    let mut data = PersonCollection::make_sample();
    println!("{:?}",data);

    data.do_some_processing();
    println!("End try_collection");
}

fn try_box() {
    println!("Start try_box");
    let place = Place {
        id: String::from("my id"),
        name: String::from("my place"),
        some_num: 1
    };
    let boxed_place = Box::new(place);
    println!("boxed_place = {:?}",boxed_place);
    
    println!("End try_box");
}

#[derive(Debug)]
struct Person {
    id: String,
    name: String,
    place: Rc<Place>
}

#[derive(Debug)]
struct Place {
    id: String,
    name: String,
    some_num: u32
}

#[derive(Debug)]
struct PersonCollection {
    persons: HashMap<String,Person>,
    places: HashMap<String,Place>
}



impl PersonCollection {
    fn make_sample() ->PersonCollection {
        let mut data = PersonCollection {
            persons: HashMap::new(),
            places: HashMap::new()
        };

        data.make_places();
   //     data.make_persons();
        data
    }

    fn make_places(&mut self) {
        let basename = "place_";
        for i in 1..5 {
            let place = Place {
                id: format!("{0}{1}",basename,i),
                name: format!("{0}{1}",basename,i),
                some_num: i
            };
            self.places.insert(place.name.clone(), place);
        }
    }

   /*  fn make_persons(&mut self) {
        let basename = "person_";
        let place_basename = "place_";
        
        for i in 1..5 {
            let place_name = format!("{0}{1}",place_basename,i);
            let place = self.places.get(&place_name)
                .unwrap()
                .clone();
            let person = Person {
                id: format!("{0}{1}",basename,i),
                name: format!("{0}{1}",basename,i),
                place: place
            };
            self.persons.insert(person.name.clone(), person);
        }
    }
    */

    fn do_some_processing(&mut self) {
        for person in self.persons.values_mut() {
            person.name.push_str("_A");
            // below is not allowed!
            //person.place.name.push_str("_B");
        //    let place = self.places.get_mut(&person.place.name).unwrap();
        //    place.name.push_str("_B");
                
                
            println!("Person {} lives in {}",person.name,person.place.name);
            
        }
    }
    
}