use std::cell::Cell;

type Year = usize;

enum Vendor {
	BMW,
    TOYOTA
}

impl Vendor {
    fn to_string(&self) -> &str {
        match self {
            Vendor::BMW => "BMW",
            Vendor::TOYOTA => "Toyota"
        }
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

pub fn main() {
	let car = {
	    let vendor = Vendor::BMW;
    	let model = Model { vendor: vendor, model: "316".to_string() };
	    Car { vendor: Cell::new(None), model: model, year: 1996 }
	};
	car.vendor.set(Some(&car.model.vendor));

    let car_2 = {
        let vendor = Vendor::TOYOTA;
        let model = Model {vendor: vendor,model: String::from("Corolla")};
        Car {vendor: Cell::new(None), model: model, year: 2005}
    };
    let vendor = Vendor::TOYOTA;
    car_2.vendor.set(Some(&vendor));

    car_2.print_vendor();

    
}