#include <Encoder.h>
#include <Keyboard.h>
// Built on a teensy 4.1, though any MCU capable of keystrokes should work.
// Intended to interface with fsTurt.py
// IO Needs debouncing.  
// Define IO
#define ENCODER1_PINA 1
#define ENCODER1_PINB 3
#define ENCODER2_PINA 5
#define ENCODER2_PINB 7
#define color_Btn     11  // g key
#define clear_Btn     27  // c key
#define lift_Btn      9   // l key
#define save_Btn      29  // s key
#define demo_Btn      31  // d
// Create encoder objects

Encoder encoder1(ENCODER1_PINA, ENCODER1_PINB);
Encoder encoder2(ENCODER2_PINA, ENCODER2_PINB);

// Variables to track encoder movement direction
int prevEncoder1Position = 0;
int prevEncoder2Position = 0;

void setup() {
  pinMode(color_Btn, INPUT_PULLUP);
  pinMode(clear_Btn, INPUT_PULLUP);
  pinMode(lift_Btn,  INPUT_PULLUP);
  pinMode(save_Btn,  INPUT_PULLUP);
  pinMode(demo_Btn,  INPUT_PULLUP);  
  
  Serial.begin(9600);
  delay(3000);
 /* 
  while (!Serial) {
    ; // Wait for serial port to connect
      // This is only for debuggig
  }
*/
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
    Keyboard.press(KEY_LEFT_ARROW);
    Keyboard.release(KEY_LEFT_ARROW);
  } else if (encoder1Direction == 1) {
    Keyboard.press(KEY_RIGHT_ARROW);
    Keyboard.release(KEY_RIGHT_ARROW);
  } else {
    Keyboard.release(KEY_RIGHT_ARROW);
    Keyboard.release(KEY_LEFT_ARROW);
  }

  if (encoder2Direction == 1) {
    Keyboard.press(KEY_UP_ARROW);
    Keyboard.release(KEY_UP_ARROW);
  } else if (encoder2Direction == -1) {
    //Serial.println("Encoder 2: Negative");
    Keyboard.press(KEY_DOWN_ARROW);
    Keyboard.release(KEY_DOWN_ARROW);
  } else {
    Keyboard.release(KEY_DOWN_ARROW);
    Keyboard.release(KEY_UP_ARROW);
  }

 
  if(digitalRead(color_Btn) == LOW){
   // Serial.println("G");
    Keyboard.press(KEY_G);
    Keyboard.release(KEY_G);
    }
  if(digitalRead(clear_Btn) == LOW){
    //Serial.println("C");
    Keyboard.press(KEY_C);
    Keyboard.release(KEY_C);
    }
    
  if(digitalRead(lift_Btn) == LOW){
    //Serial.println("L");
    Keyboard.press(KEY_L);
    Keyboard.release(KEY_L);
    }
/* 
  if(digitalRead(save_Btn) == LOW){
    Serial.println("S");
    //Keyboard.press(KEY_S);
    //Keyboard.release(KEY_S);
    delay(3000); //can we save a file in 3s?
    } 

  if(digitalRead(demo_Btn) == LOW){
    Serial.println("D");
    //Keyboard.press(KEY_D);
    //Keyboard.release(KEY_D);
    }   
*/
  // Delay to prevent spamming
  delay(100);
}
