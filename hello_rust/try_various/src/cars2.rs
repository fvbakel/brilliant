use std::cell::Cell;

type Year = usize;

struct Vendor {
	name: String
}

impl Vendor {
    fn to_string(&self) -> &str {
        &self.name
    }
}

struct Model {
	vendor: Vendor,
	model: String,
}

struct Car<'a> {
	vendor: Cell<Option<&'a Vendor>>,
	model: Model,
	year: Year,
}

impl<'a> Car<'a> {
    fn print_vendor(&self) {
        match self.vendor.get() {
            Some(vendor) => println!("The vendor is {}",vendor.to_string()),
            None =>  println!("The vendor is not set"),
        };
    }
}

fn get_car<'a> ()-> Car<'a> {
    let car_3 = {
	    let vendor = Vendor {
            name: String::from("Hunday")
        };
        let model = Model {vendor: vendor,model: String::from("Corolla")};
        Car {vendor: Cell::new(None), model: model, year: 2005}
    };
    // vendor can not be set inside this function!
    //car_3.vendor.set(Some(&car_3.model.vendor));
    car_3
}

fn get_car_2<'a>() -> Car<'a> {
    let car = get_car();
    // also not allowed in this function
   // car.vendor.set(Some(&car.model.vendor));
    car
}

//
// also not allowed?
/* fn set_vendor(car:&mut Car,vendor: &Vendor) {
    car.vendor.set(Some(vendor));
}

*/

pub fn main() {
    println!("Start cars 2");
	let car = {
	    let vendor = Vendor {
            name: String::from("BMW")
        };
    	let model = Model { vendor: vendor, model: "316".to_string() };
	    Car { vendor: Cell::new(None), model: model, year: 1996 }
	};
	car.vendor.set(Some(&car.model.vendor));
    car.print_vendor();

    let car_2 = {
	    let vendor = Vendor {
            name: String::from("Toyota")
        };
        let model = Model {vendor: vendor,model: String::from("Corolla")};
        Car {vendor: Cell::new(None), model: model, year: 2005}
    };
    let vendor = Vendor {
        name: String::from("Toyota")
    };
    car_2.vendor.set(Some(&vendor));

    car_2.print_vendor();

    let car_3 = get_car();
    car_3.vendor.set(Some(&car_3.model.vendor));
    car_3.print_vendor();

    let car_4 = get_car_2();
    car_4.print_vendor();

}