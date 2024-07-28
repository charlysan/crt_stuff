#define DO_NOT_PULL_SDA_SCL_DOWN_AT_INIT 1

// YPbPr2RGB i2c switcher for Panasonic TC-21FX30LA (Micronas VCT-49xyI)
// Ver. 0.1 - July 20204

#include <ESP8266WiFi.h>
#include <esp_i2c.h>


#define SCL_LOW_PULL_MS 300  // Pull down SCL for X ms
#define SCL_HIGH_WAIT_MS 200 // Wait until SCL stays high for at least X ms
#define I2C_CLOCK 50000L     // I2C clock 50 KHz

const uint8_t VSP_ADDR = 0x58;

const uint8_t SDA_PIN = D2;
const uint8_t SCL_PIN = D1;

volatile unsigned long sclHighTimer = 0;
volatile bool sclHigh = false;


void ICACHE_RAM_ATTR handleSCLChange() {
  if (digitalRead(SCL_PIN) == HIGH) {
    sclHighTimer = millis(); // Start the timer when SCL goes high
    sclHigh = true;
  } else {
    sclHigh = false;
  }
}

void setup() {
  // Pin Setup
  pinMode(SDA_PIN, INPUT_PULLUP);
  pinMode(SCL_PIN, INPUT_PULLUP);

  // Disable WiFi
  WiFi.mode(WIFI_OFF);

  esp_i2c_init(SDA_PIN, SCL_PIN);
  esp_i2c_set_clock(I2C_CLOCK);
  
  // Interrupt to detect SCL state change
  attachInterrupt(digitalPinToInterrupt(SCL_PIN), handleSCLChange, CHANGE);

  // Pull the SCL pin low for 300ms
  pinMode(SCL_PIN, OUTPUT);
  digitalWrite(SCL_PIN, LOW);
  delay(SCL_LOW_PULL_MS);
  pinMode(SCL_PIN, INPUT_PULLUP);

  // Initialize timer
  sclHighTimer = millis();

  // Wait until SCL stays high for at least SCL_HIGH_WAIT_MS
  while (true) {
    if (sclHigh && (millis() - sclHighTimer) > SCL_HIGH_WAIT_MS) {
      uint8_t dataToSend[3];

      // YUVSEL -> RGB: 0x4b 0x81 0x08 
      dataToSend[0] = 0x4b;
      dataToSend[1] = 0x81;
      dataToSend[2] = 0x08;
      esp_i2c_write_buf(VSP_ADDR, dataToSend, 3, 1);
      
      // ADC_SEL -> 6: 0x49 0xd7 0x5c 
      dataToSend[0] = 0x49;
      dataToSend[1] = 0xd7;
      dataToSend[2] = 0x5c;
      esp_i2c_write_buf(VSP_ADDR, dataToSend, 3, 1);
    
      // VINSEL6 -> 7: 0x3f 0x4a 0x07 
      dataToSend[0] = 0x3f;
      dataToSend[1] = 0x4a;
      dataToSend[2] = 0x07;
      esp_i2c_write_buf(VSP_ADDR, dataToSend, 3, 1);

      break;
    }
  }
}

void loop() {
}
