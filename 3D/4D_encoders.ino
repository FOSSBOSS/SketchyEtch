
#include <Wire.h>
#include "Adafruit_seesaw.h"
#include <seesaw_neopixel.h>
#include <Keyboard.h>
/*example code with neopixels purged, and teensy printf statments added*/

#define SS_SWITCH        24      // this is the pin on the encoder connected to switch
#define SEESAW_BASE_ADDR          0x36  // I2C address, starts with 0x36

Adafruit_seesaw encoders[4];

int32_t encoder_positions[] = {0, 0, 0, 0};
bool found_encoders[] = {false, false, false, false};

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

    // set encoder to 0
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
  for (uint8_t enc=0; enc<sizeof(found_encoders); enc++) {
     if (found_encoders[enc] == false) continue;

     int32_t new_position = encoders[enc].getEncoderPosition();
     // did we move around?
     if (encoder_positions[enc] != new_position) {
       Serial.printf("E1: %ld, E2: %ld, E3: %ld, E4: %ld\n",encoders[0],encoders[1],encoders[2],encoders[3]);
       Serial.println(new_position);         // display new position
       encoder_positions[enc] = new_position;
     }

     if (! encoders[enc].digitalRead(SS_SWITCH)) {
        Serial.printf("E#%d pressed\n",enc);
     }
  }

  // don't overwhelm serial port
  yield();
  delay(10);
}
