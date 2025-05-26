#include <Wire.h>
#include "Adafruit_seesaw.h"
#include <Keyboard.h>

/*Tenative idea is to have X,Y,Z, and view select*/

#define SS_SWITCH        24      // this is the pin on the encoder connected to switch
#define SEESAW_BASE_ADDR          0x36  // I2C address, starts with 0x36
const uint8_t Nencoders = 5;
Adafruit_seesaw encoders[Nencoders];

unsigned long btn_press[Nencoders] = {0, 0, 0, 0, 0};
const unsigned long dbd = 200; // deBouce delay = 100 ms

int32_t encoder_positions[] = {0, 0, 0, 0, 0};
bool found_encoders[] = {false, false, false, false, false};

void setup() {
  Serial.begin(115200);
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

    encoders[enc].setGPIOInterrupts((uint32_t)1 << SS_SWITCH, 1);
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
unsigned long now = millis(); 
  for (uint8_t enc=0; enc<sizeof(found_encoders); enc++) {
     if (found_encoders[enc] == false) continue;

     int32_t new_position = encoders[enc].getEncoderPosition();
     // did we move around?
     if (encoder_positions[enc] != new_position) {
      encoder_positions[enc] = new_position; // update position before printing
      //Serial.printf("X: %ld, Y: %ld, Z: %ld, E4: %ld\n", encoder_positions[0],encoder_positions[1],encoder_positions[2],encoder_positions[3]);
      Serial.printf("X: %ld, Y: %ld, Z: %ld, R: %ld , V: %ld \n", encoder_positions[0],encoder_positions[1],encoder_positions[2],encoder_positions[3],encoder_positions[4]);            
     }

     if (! encoders[enc].digitalRead(SS_SWITCH)){
        if(now - btn_press[enc] > dbd){        
        Serial.printf("E#%d pressed\n",enc);
        Serial.flush(); //teensy serial is too fast. wait for the print statment then set debounce time
        btn_press[enc] = now;
     }
     }
  }


  // don't overwhelm serial port
  yield(); //delay calls yield
  delay(10);
}
