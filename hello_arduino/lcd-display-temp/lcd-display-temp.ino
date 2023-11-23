#include <LiquidCrystal_I2C.h>
#include "dht11.h"

const int totalColumns = 20;
const int totalRows = 4;
const int temperatureRow = 0;
const int humidityRow = 2;

const int dht11Pin = 4;
const int buttonPin = 2;

bool isDisplayOn = true;
int buttonState = 0; 

LiquidCrystal_I2C lcd(0x27, totalColumns, totalRows);  

dht11 DHT11;

void setup() {
  lcd.init();
  lcd.backlight();
  lcd.setCursor(3,0);
  lcd.print("WELCOME");
  delay(1000);
  lcd.clear();
  lcd.setCursor(0,temperatureRow);
  lcd.print("Temparature (C):");
  
  lcd.setCursor(0,humidityRow);
  lcd.print("Humidity (%):");

  pinMode(buttonPin, INPUT);

}

void loop() {
  if (isDisplayOn) {
    int chk = DHT11.read(dht11Pin);
  
    displayTemperature(DHT11.temperature);
    displayHumidity(DHT11.humidity);
  }
  buttonState = digitalRead(buttonPin);

  if (buttonState == HIGH ) {
    if (isDisplayOn) {
      lcd.backlight();
      isDisplayOn = false;
    } else {
      lcd.noBacklight();
      isDisplayOn = true;
    }
    delay(200);
  }

}

void displayTemperature(float temperature) {
  lcd.setCursor(0,temperatureRow + 1);
  lcd.print( temperature, 2);
}

void displayHumidity(float humidity) {
  lcd.setCursor(0,humidityRow + 1);
  lcd.print(humidity, 2);
}
