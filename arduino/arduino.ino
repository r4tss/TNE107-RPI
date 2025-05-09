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

  sensor.init();
  sensor.setMeasurementTimingBudget(10000);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(2, 0);
  lcd.print("AGV booting!");
  received = "Dot dot dot dot";
}

void loop() {
  
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
    analogWrite(D1, 150);
    digitalWrite(D2, LOW);
    analogWrite(D3, 150);
    digitalWrite(D4, LOW);
  }
  else if (received.indexOf("Backward") >= 0) { // Backward
    digitalWrite(D1, LOW);
    analogWrite(D2, 150);
    digitalWrite(D3, LOW);
    analogWrite(D4, 150);
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
    dist = sensor.readRangeSingleMillimeters();
    if (dist < 50) {
      Serial.println("Something in front!");
      received = "Check1";
      analogWrite(D1, 255);
      digitalWrite(D2, LOW);
      digitalWrite(D3, LOW);
      analogWrite(D4, 255);
      delay(100);
      digitalWrite(D1, LOW);
      digitalWrite(D2, LOW);
      digitalWrite(D3, LOW);
      digitalWrite(D4, LOW);
      delay(500);
    }
    else if (digitalRead(RIR)) {
      delay(50);
      analogWrite(D1, 255);
      digitalWrite(D2, LOW);
      digitalWrite(D3, LOW);
      analogWrite(D4, 255);
      delay(100);
    }
    else if (digitalRead(LIR)) {
      delay(50);
      digitalWrite(D1, LOW);
      analogWrite(D2, 255);
      analogWrite(D3, 255);
      digitalWrite(D4, LOW);
      delay(100);
    }
    else {
      analogWrite(D1, 50);
      digitalWrite(D2, LOW);
      analogWrite(D3, 50);
      digitalWrite(D4, LOW);
    }
  }
  else if (received.indexOf("Check1") >= 0) {
    received = "Check2";
    digitalWrite(D1, LOW);
    analogWrite(D2, 100);
    analogWrite(D3, 100);
    digitalWrite(D4, LOW);
    delay(100 + i);
    digitalWrite(D1, LOW);
    digitalWrite(D2, LOW);
    digitalWrite(D3, LOW);
    digitalWrite(D4, LOW);
    delay(500);

    i += 10;
  }
  else if (received.indexOf("Check2") >= 0) {
    received = "Check1";
    analogWrite(D1, 100);
    digitalWrite(D2, LOW);
    digitalWrite(D3, LOW);
    analogWrite(D4, 100);
    delay(100 + i);
    digitalWrite(D1, LOW);
    digitalWrite(D2, LOW);
    digitalWrite(D3, LOW);
    digitalWrite(D4, LOW);
    delay(500);

    i += 10;
  }
  else {
    i = 0;
    digitalWrite(D1, LOW);
    digitalWrite(D2, LOW);
    digitalWrite(D3, LOW);
    digitalWrite(D4, LOW);
  }

  if (i > 100) {
    received = "Stop";
  }
}
