#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#define PIN 9
#define NUMPIXELS 12
const byte numChars = 16;
char receivedChars[numChars];
int incomingByte;
static byte ndx = 0;
Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_RGB + NEO_KHZ400);
void decoder(char* received);
void light_up_led(int led, int red, int green, int blue);
void setup() {
  Serial.begin(115200);
  strip.begin();
  strip.fill(strip.Color(0, 0, 0));
  strip.show();
}

void loop() {
  if (Serial.available() > 0) {
    incomingByte = Serial.read();
    if (incomingByte != '\n' && ndx < numChars){
      receivedChars[ndx] = (char)incomingByte;
      ndx++;
    }
    else{
      ndx = 0;
      decoder(receivedChars);
      memset(receivedChars, 0, sizeof(receivedChars));
    }
  }
}

void decoder(char* received) {
  // Serial.println(received);
  char* inputs = strtok(received, ":");
  int values[4];
  for(int i = 0; i<4; i++){
    values[i] = atoi(inputs);
    inputs = strtok(0, ":");
    // Serial.println(values[i]);
  }
  light_up_led(values[0], values[1], values[2], values[3]);
  // Serial.println("Lit");
}

void light_up_led(int led, int red, int green, int blue) {
  // Serial.print("LED: ");
  // Serial.println(led);
  // Serial.print("Red: ");
  // Serial.println(red);
  // Serial.print("Green: ");
  // Serial.println(green);
  // Serial.print("Blue: ");
  // Serial.println(blue);
  strip.setPixelColor(led, strip.Color(red, green, blue));
  strip.show();
}