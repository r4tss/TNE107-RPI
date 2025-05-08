#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <VL53L0X.h>

// To H-bridges
const int D1 = 9;
const int D2 = 3;
const int D3 = 6;
const int D4 = 5;

// UART communication
char c;
String received = "";

// LCD
LiquidCrystal_I2C lcd(0x27, 20, 4);
int emptySpace = 0;

// TOF
VL53L0X sensor;
int dist = 0;

// IR
const int LIR = 10;
const int RIR = 11;

void setup() {
  pinMode(D1, OUTPUT);
  pinMode(D2, OUTPUT);
  pinMode(D3, OUTPUT);
  pinMode(D4, OUTPUT);

  pinMode(LIR, INPUT);
  pinMode(RIR, INPUT);

  digitalWrite(D1, LOW);
  digitalWrite(D2, LOW);
  digitalWrite(D3, LOW);
  digitalWrite(D4, LOW);

  Serial.begin(115200);

  Wire.begin();
  lcd.init();
  lcd.backlight();
  lcd.setCursor(2, 0);
  lcd.print("AGV booting!");
  received = "Dot dot dot dot";

  
  sensor.setTimeout(500);
  if (!sensor.init())
  {
    Serial.println("Failed to detect and initialize sensor!");
    while (1) {}
  }
  sensor.setMeasurementTimingBudget(10000);
}

void loop() {
  dist = sensor.readRangeSingleMillimeters();

  if (Serial.available() > 0) {
    received = Serial.readStringUntil('\n');
    //Serial.println(received);
  }

  if (received.indexOf("Bluetooth up") >= 0) {
    lcd.clear();
    lcd.setCursor(2, 0);
    lcd.print("Bluetooth up");
    lcd.setCursor(6, 1);
    lcd.print("....");
    emptySpace = 0;
    received = "Dot dot dot dot"; // Reset received message so that LCD does not clear and rewrite every tick
  }

  if (received.indexOf("Dot dot dot dot") >= 0) {
    String dot;
    for (int i = 0;i < 4;i++) {
      if (i == emptySpace) {
        dot = " ";
      } else {
        dot = ".";
      }
      lcd.setCursor(6 + i, 1);
      lcd.print(dot);
    }
    emptySpace++;
    if (emptySpace > 3) {
      emptySpace = 0;
    }
    delay(500);
  }

  if (received.indexOf("Bluetooth connected") >= 0) {
    lcd.clear();
    lcd.setCursor(2, 0);
    lcd.print("Connected to");
    lcd.setCursor(2, 1);
    lcd.print(received.substring(20, 32)); // Message as 'Bluetooth connected XXXXXXXXXXXX' with MAC-address.
    received = "";
    delay(2000);
    lcd.clear();
  }

  if (received.indexOf("Closing down") >= 0) {
    lcd.clear();
    lcd.setCursor(1, 0);
    lcd.print("Shutting down!");
    received = "Dot dot dot dot";

    digitalWrite(D1, LOW);
    digitalWrite(D2, LOW);
    digitalWrite(D3, LOW);
    digitalWrite(D4, LOW);
  }

  if (received.indexOf("Forward") >= 0) { // Forward
    digitalWrite(D1, HIGH);
    digitalWrite(D2, LOW);
    digitalWrite(D3, HIGH);
    digitalWrite(D4, LOW);
  }
  else if (received.indexOf("Backward") >= 0) { // Backward
    digitalWrite(D1, LOW);
    digitalWrite(D2, HIGH);
    digitalWrite(D3, LOW);
    digitalWrite(D4, HIGH);
  }
  else if (received.indexOf("Right") >= 0) { // Right
    digitalWrite(D1, HIGH);
    digitalWrite(D2, LOW);
    digitalWrite(D3, LOW);
    digitalWrite(D4, HIGH);
  }
  else if (received.indexOf("Left") >= 0) { // Left
    digitalWrite(D1, LOW);
    digitalWrite(D2, HIGH);
    digitalWrite(D3, HIGH);
    digitalWrite(D4, LOW);
  }
  else if (received.indexOf("Goal") >= 0) { // Pair with goal
    if (((digitalRead(LIR)) && digitalRead(RIR)) || (dist < 100)) {
      Serial.println("Stopped");
      digitalWrite(D1, LOW);
      digitalWrite(D2, LOW);
      digitalWrite(D3, LOW);
      digitalWrite(D4, LOW);
    }
    else if (digitalRead(RIR)) {
      analogWrite(D1, 100);
      digitalWrite(D2, LOW);
      digitalWrite(D3, LOW);
      analogWrite(D4, 100);
    }
    else if (digitalRead(LIR)) {
      digitalWrite(D1, LOW);
      analogWrite(D2, 100);
      analogWrite(D3, 100);
      digitalWrite(D4, LOW);
    }
    else {
      analogWrite(D1, 50);
      digitalWrite(D2, LOW);
      analogWrite(D3, 50);
      digitalWrite(D4, LOW);
    }
  } 
  else {
    digitalWrite(D1, LOW);
    digitalWrite(D2, LOW);
    digitalWrite(D3, LOW);
    digitalWrite(D4, LOW);
  }

  
  
}
