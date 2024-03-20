#include <Encoder.h>
#include <Keyboard.h>
#include <Bounce2.h>
// Define IO
#define ENCODER1_PINA 1
#define ENCODER1_PINB 3
#define ENCODER2_PINA 5
#define ENCODER2_PINB 7
#define color_Btn     11  // g key
#define clear_Btn     27  // c key
#define lift_Btn      9   // l key
#define save_Btn      29  // s key
#define demo_Btn      31  // d key
// Create encoder objects
Encoder encoder1(ENCODER1_PINA, ENCODER1_PINB);
Encoder encoder2(ENCODER2_PINA, ENCODER2_PINB);
// Create Bounce objects for buttons
Bounce colorButton = Bounce();
Bounce clearButton = Bounce();
Bounce liftButton  = Bounce();
Bounce saveButton  = Bounce();
Bounce demoButton  = Bounce();
// Variables to track encoder movement direction
int prevEncoder1Position = 0;
int prevEncoder2Position = 0;

void setup() {

  int bounceTime = 5;
  // Attach buttons to Bounce objects and set debounce interval
  colorButton.attach(color_Btn, INPUT_PULLUP);
  colorButton.interval(bounceTime);

  clearButton.attach(clear_Btn, INPUT_PULLUP);
  clearButton.interval(bounceTime);

  liftButton.attach(lift_Btn, INPUT_PULLUP);
  liftButton.interval(bounceTime);

  saveButton.attach(save_Btn, INPUT_PULLUP);
  saveButton.interval(bounceTime);

  demoButton.attach(demo_Btn, INPUT_PULLUP);
  demoButton.interval(bounceTime);  
  Serial.begin(9600);
  delay(3000); 
/*
  while (!Serial) {
    ; // Wait for serial port to connect
      // This is only for debuggig
  }
*/
Serial.println("Sketchy Etch initialied");
  Keyboard.begin();
}

void loop() {
  // Read encoder positions
  int encoder1Position = encoder1.read();
  int encoder2Position = encoder2.read();

  // Detect encoder 1 movement direction
  int encoder1Direction = 0;
  if (encoder1Position > prevEncoder1Position) {
    encoder1Direction = 1; // Positive direction
  } else if (encoder1Position < prevEncoder1Position) {
    encoder1Direction = -1; // Negative direction
  }

  // Detect encoder 2 movement direction
  int encoder2Direction = 0;
  if (encoder2Position > prevEncoder2Position) {
    encoder2Direction = 1; // Positive direction
  } else if (encoder2Position < prevEncoder2Position) {
    encoder2Direction = -1; // Negative direction
  }

  // Update previous positions for next iteration
  prevEncoder1Position = encoder1Position;
  prevEncoder2Position = encoder2Position;

  // Use encoder direction variables to perform actions
  if (encoder1Direction == -1) {
    //Serial.println("LEFT");
    Keyboard.press(KEY_LEFT_ARROW);
    Keyboard.release(KEY_LEFT_ARROW);
  } else if (encoder1Direction == 1) {
    //Serial.println("RiGHT");
    Keyboard.press(KEY_RIGHT_ARROW);
    Keyboard.release(KEY_RIGHT_ARROW);
  } else {
    Keyboard.release(KEY_RIGHT_ARROW);
    Keyboard.release(KEY_LEFT_ARROW);
  }

  if (encoder2Direction == 1) {
    //Serial.println("UP");
    Keyboard.press(KEY_UP_ARROW);
    Keyboard.release(KEY_UP_ARROW);
  } else if (encoder2Direction == -1) {
    //Serial.println("DOWN");
    Keyboard.press(KEY_DOWN_ARROW);
    Keyboard.release(KEY_DOWN_ARROW);
  } else {
    Keyboard.release(KEY_DOWN_ARROW);
    Keyboard.release(KEY_UP_ARROW);
  }

  // Handle button presses with debouncing
  colorButton.update();
  if (colorButton.fell()) {
    //Serial.println("Color Change");
    Keyboard.press(KEY_G);
    Keyboard.release(KEY_G);
    }
  
  clearButton.update();
  if (clearButton.fell()) {  
    //Serial.println("CLEAR");
    Keyboard.press(KEY_C);
    Keyboard.release(KEY_C);
    }
  
  liftButton.update();
  if (liftButton.fell()) {  
    //Serial.println("LIFT");
    Keyboard.press(KEY_L);
    Keyboard.release(KEY_L);
    }
  saveButton.update();
  if (saveButton.fell()) {
    Serial.println("Saving file");
    Keyboard.press(KEY_S);
    Keyboard.release(KEY_S);
    delay(5000); //Really want to prevent spamming this one.
    Serial.println("Saving Complete"); 
    } 

  demoButton.update();
  if (demoButton.fell()) {
    Serial.println("DEMOLITION");
    Keyboard.press(KEY_D);
    Keyboard.release(KEY_D);
    }   
/**/
  // Delay to prevent spamming
  delay(70);
}
