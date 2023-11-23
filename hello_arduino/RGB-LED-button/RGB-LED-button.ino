// see https://arduinogetstarted.com/tutorials/arduino-rgb-led

const int PIN_RED   = 5;
const int PIN_GREEN = 6;
const int PIN_BLUE  = 9;

const int buttonPin = 2;     // the number of the pushbutton pin
int buttonState = 0;

enum mode {OFF,RED,GREEN,BLUE,WHITE};

mode current_mode = RED;

void setup() {
  // put your setup code here, to run once:
  pinMode(PIN_RED,   OUTPUT);
  pinMode(PIN_GREEN, OUTPUT);
  pinMode(PIN_BLUE,  OUTPUT);
  pinMode(buttonPin, INPUT);

  Serial.begin(9600);

  setCurrentMode(RED);
  delay(100);
  setCurrentMode(GREEN);
  delay(100);
  setCurrentMode(BLUE);
  delay(100);
  setCurrentMode(WHITE);
  delay(100);
  setCurrentMode(OFF);
  delay(100);
}

void loop() {
   // read the state of the pushbutton value:
   buttonState = digitalRead(buttonPin);

   if (buttonState == HIGH) {

     mode new_mode = getNextMode();
     setCurrentMode(new_mode);
     
     delay(1000);
   }
}

mode getNextMode() {
  if (current_mode == WHITE) {
    return OFF;
  }
  return current_mode + 1;

}


void setCurrentMode(mode new_mode) {
  current_mode = new_mode;
  switch (current_mode) {
    case OFF:
      setColor(0,0,0);
      break;
    case RED:
      setColor(255,0,0);
      break;
    case GREEN:
      setColor(0,255,0);
      break;
    case BLUE:
      setColor(0,0,255);
      break;
    case WHITE:
      setColor(255,255,255);
      break;
  }
    
}

void setColor(int R, int G, int B) {
  analogWrite(PIN_RED,   R);
  analogWrite(PIN_GREEN, G);
  analogWrite(PIN_BLUE,  B);
}
