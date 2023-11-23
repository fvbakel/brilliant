#include <LiquidCrystal_I2C.h>

const int totalColumns = 20;
const int totalRows = 4;

LiquidCrystal_I2C lcd(0x27, totalColumns, totalRows);  

String staticMessage = "I2C LCD Tutorial";
String scrollingMessage = "Welcome to Microcontrollerslab! This is a scrolling message.";

void scrollMessage(int row, String message, int delayTime, int totalColumns) {
  for (int i=0; i < totalColumns; i++) {
    message = " " + message;  
  } 
  message = message + " "; 
  for (int position = 0; position < message.length(); position++) {
    lcd.setCursor(0, row);
    lcd.print(message.substring(position, position + totalColumns));
    delay(delayTime);
  }
}

void setup() {
  // put your setup code here, to run once:
  lcd.init();                      // initialize the lcd 
  // Print a message to the LCD.
  lcd.backlight();
  lcd.setCursor(3,0);
  lcd.print("Hello, world!");
  delay(2000);
  lcd.noBacklight();
  delay(1000);
  lcd.backlight();
  lcd.clear();
  

}

void loop() {
  lcd.setCursor(0, 0);
  lcd.print(staticMessage);
  scrollMessage(1, scrollingMessage, 250, totalColumns);

}
