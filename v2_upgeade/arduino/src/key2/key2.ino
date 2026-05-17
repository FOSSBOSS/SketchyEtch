#include <Encoder.h>
#include <Keyboard.h>
#include <Bounce2.h>
#include <Wire.h>
#include "Adafruit_seesaw.h"
#include <Keyboard.h>

#define SS_SWITCH        24      // this is the pin on the encoder connected to switch
#define SEESAW_BASE_ADDR          0x36  // I2C address, starts with 0x36
const uint8_t Nencoders = 2;
Adafruit_seesaw encoders[Nencoders];

unsigned long btn_press[Nencoders] = {0, 0};
const unsigned long dbd = 200; // deBouce delay = 100 ms
int32_t encoder_positions[] = {0, 0};
bool found_encoders[] = {false, false};
#define color_Btn     1  // g key
#define clear_Btn     2  // c key
#define lift_Btn      3  // l key
#define save_Btn      4  // s key
#define demo_Btn      5  // d key

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

  pinMode(0, OUTPUT);
  digitalWrite(0,LOW); // use io as reference.
  Serial.begin(115200);
 // forgot the buttons lol
  pinMode(color_Btn, INPUT_PULLUP);
  pinMode(clear_Btn, INPUT_PULLUP);
  pinMode(lift_Btn,  INPUT_PULLUP);
  pinMode(save_Btn,  INPUT_PULLUP);
  pinMode(demo_Btn,  INPUT_PULLUP);

  colorButton.attach(color_Btn);
  clearButton.attach(clear_Btn);
  liftButton.attach(lift_Btn);
  saveButton.attach(save_Btn);
  demoButton.attach(demo_Btn);

  colorButton.interval(25);
  clearButton.interval(25);
  liftButton.interval(25);
  saveButton.interval(25);
  demoButton.interval(25);
  Wire.begin();
  while (!Serial) delay(10);

bool all_found = true;
for (uint8_t enc = 0; enc < sizeof(found_encoders); enc++) {
  uint8_t addr = SEESAW_BASE_ADDR + enc;

  if (!encoders[enc].begin(addr)) {
    Serial.printf("Couldn't find encoder #%d (0x%02X)\n", enc, addr);
    found_encoders[enc] = false;
    all_found = false;
  } else {
    encoders[enc].pinMode(SS_SWITCH, INPUT_PULLUP);

    // Reset encoder to 0
    encoders[enc].setEncoderPosition(0);
    encoder_positions[enc] = 0;

    //encoders[enc].setGPIOInterrupts((uint32_t)1 << SS_SWITCH, 1);
    encoders[enc].enableEncoderInterrupt();
    found_encoders[enc] = true;
  }
}
  if (all_found) {
    Serial.print("All encoders found at addresses: ");
    for (uint8_t enc = 0; enc < sizeof(found_encoders); enc++) {
      Serial.printf("0x%02X ", SEESAW_BASE_ADDR + enc);
    }
    Serial.println();
  }
}

void loop() {
//unsigned long now = millis(); 
  for (uint8_t enc=0; enc<sizeof(found_encoders); enc++) {
     if (found_encoders[enc] == false) continue;

     int32_t new_position = encoders[enc].getEncoderPosition();
     // did we move around?
     if (encoder_positions[enc] != new_position) {
      encoder_positions[enc] = new_position; // update position before printing
    // Serial.printf("X: %ld, Y: %ld \n", encoder_positions[0],encoder_positions[1]);            

  int encoder1Position = encoder_positions[0];
  int encoder2Position = encoder_positions[1];
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

  prevEncoder1Position = encoder1Position;
  prevEncoder2Position = encoder2Position;

  // Use encoder direction variables to perform actions
  if (encoder1Direction == -1) {
   // Serial.println("LEFT");
    Keyboard.press(KEY_LEFT_ARROW);
    Keyboard.release(KEY_LEFT_ARROW);
  } else if (encoder1Direction == 1) {
    // Serial.println("RiGHT");
    Keyboard.press(KEY_RIGHT_ARROW);
    Keyboard.release(KEY_RIGHT_ARROW);
  } else {
    Keyboard.release(KEY_RIGHT_ARROW);
    Keyboard.release(KEY_LEFT_ARROW);
  }

  if (encoder2Direction == 1) {
    Serial.println("UP");
    Keyboard.press(KEY_UP_ARROW);
    Keyboard.release(KEY_UP_ARROW);
  } else if (encoder2Direction == -1) {
    Serial.println("DOWN");
    Keyboard.press(KEY_DOWN_ARROW);
    Keyboard.release(KEY_DOWN_ARROW);
  } else {
    Keyboard.release(KEY_DOWN_ARROW);
    Keyboard.release(KEY_UP_ARROW);
  }
     
  }
    // Handle button presses with debouncing
  colorButton.update();
  if (colorButton.fell()) {
    Serial.println("Color Change");
    Keyboard.press(KEY_G);
    Keyboard.release(KEY_G);
    }
  
  clearButton.update();
  if (clearButton.fell()) {  
    Serial.println("CLEAR");
    Keyboard.press(KEY_C);
    Keyboard.release(KEY_C);
    }
  
  liftButton.update();
  if (liftButton.fell()) {  
    Serial.println("LIFT");
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
  }  
  delay(10);
}
