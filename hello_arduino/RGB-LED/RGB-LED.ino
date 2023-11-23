// see https://arduinogetstarted.com/tutorials/arduino-rgb-led

const int PIN_RED   = 5;
const int PIN_GREEN = 6;
const int PIN_BLUE  = 9;


enum mode {RED,GREEN,BLUE};

int current_red   = 0;
int current_green = 0;
int current_blue  = 0;
mode current_mode = RED;

void setup() {
  // put your setup code here, to run once:
  pinMode(PIN_RED,   OUTPUT);
  pinMode(PIN_GREEN, OUTPUT);
  pinMode(PIN_BLUE,  OUTPUT);

  Serial.begin(9600);

    // start sequence
  setColor(0,0,0);
  delay(500);
  setColor(255,0,0);
  delay(500);
  setColor(0,255,0);
  delay(500);
  setColor(0,0,255);
  delay(500);
  setColor(255,255,255);
  delay(500);
  

}

void loop() {

   current_red   = current_red + 3;
   current_green = current_green + 2;
   current_blue  = current_blue + 1;
     
   current_red   = max_255(current_red);
   current_green = max_255(current_green);
   current_blue  = max_255(current_blue);


   to_serial();
   setColor(current_red,current_green,current_blue);
}

void to_serial () {
   Serial.print("blue:");
   Serial.print(current_blue);
   Serial.print(",");
   Serial.print("red:");
   Serial.print(current_red);
   Serial.print(",");
   Serial.print("green:");
   Serial.print(current_green);
   Serial.println();
}

void all_colors () {
  if (current_mode == RED) {
    current_red = current_red + 1;
    current_green = 0;
    current_blue = 0;
    current_mode = GREEN;
  } else {
    if (current_mode == GREEN) {
      current_green = current_green + 1;
      if (current_green == 255) {
        current_mode = RED;
      } else {
        current_blue = 0;
        current_mode = BLUE;
      }
    }
    if (current_mode == BLUE) {
      current_blue = current_blue + 1;
      if (current_blue == 255) {
        current_mode = GREEN;
      }
    }
  }
  
  // put your main code here, to run repeatedly:
  current_red   = max_255(current_red);
  current_green = max_255(current_green);
  current_blue  = max_255(current_blue);


  setColor(current_red,current_green,current_blue);
}

int max_255(int color) {

  if (color > 255) {
    return 0;    
  }
  return color;
  
}

void setColor(int R, int G, int B) {
  analogWrite(PIN_RED,   R);
  analogWrite(PIN_GREEN, G);
  analogWrite(PIN_BLUE,  B);
}
