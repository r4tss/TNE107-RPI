#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <VL53L0X.h>

// To H-bridges
const int D1 = 9;
const int D2 = 3;
const int D3 = 6;
const int D4 = 5;

// UART communication and 
char c;
String received = "";
String hostAddr = "";
String xstatus = "0000";
String ystatus = "0000";
String dir = "000";

enum statusDialog { booting, btUp, btConnected, shutDown, startingGoal, foundGoal, currentStatus, obstruction };
enum availCommand { forward, backward, right, left, goal, checkRight, checkLeft, stop };

statusDialog status;
availCommand command;

// LCD
LiquidCrystal_I2C lcd(0x27, 20, 4);
int emptySpace = 0;
int i = 0;
bool dots = false;

// TOF
VL53L0X sensor;
int dist = 0;

// IR
const int FLIR = 7;
const int LIR = 10;
const int RIR = 11;
const int FRIR = 8;

void setup() {
  pinMode(D1, OUTPUT);
  pinMode(D2, OUTPUT);
  pinMode(D3, OUTPUT);
  pinMode(D4, OUTPUT);

  pinMode(FLIR, INPUT);
  pinMode(LIR, INPUT);
  pinMode(RIR, INPUT);
  pinMode(FRIR, INPUT);

  digitalWrite(D1, LOW);
  digitalWrite(D2, LOW);
  digitalWrite(D3, LOW);
  digitalWrite(D4, LOW);

  Serial.begin(115200);
  while (!Serial) { ; }
  Wire.begin();

  sensor.init();
  sensor.setMeasurementTimingBudget(100);

  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(2, 0);
  lcd.print("AGV booting!");
  dots = true;

  status = booting;
  command = stop;
}

void loop() {
  if (Serial.available() > 0) {
    received = Serial.readStringUntil('\n');
    // Serial.println(received);
  }

  // Status states handling
  if (received == "Bluetooth up") {
    status = btUp;
    dots = true;

    lcd.clear();
    lcd.setCursor(2, 0);
    lcd.print("Bluetooth up");
    lcd.setCursor(6, 1);
  }
  else if (received.indexOf("Bluetooth connected") >= 0) {
    status = btConnected;
    hostAddr = received.substring(20, 32);
    dots = false;

    lcd.clear();
    lcd.setCursor(2, 0);
    lcd.print("Connected to");
    lcd.setCursor(2, 1);
    lcd.print(hostAddr); // Message as 'Bluetooth connected XXXXXXXXXXXX' with MAC-address.
  }
  else if (received == "Closing down") {
    status = shutDown;
    dots = true;

    lcd.clear();
    lcd.setCursor(1, 0);
    lcd.print("Shutting down!");

    digitalWrite(D1, LOW);
    digitalWrite(D2, LOW);
    digitalWrite(D3, LOW);
    digitalWrite(D4, LOW);

    delay(5000);

    lcd.clear();
    lcd.setCursor(2, 0);
    lcd.print("AGV booting!");
  }
  else if (received == "Start goal") {
    status = startingGoal;
    dots = true;

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Looking for goal");
  }
  else if (received == "Found goal") {
    status = foundGoal;
    dots = false;

    lcd.clear();
    lcd.setCursor(3, 0);
    lcd.print("Found goal");
  }
  else if (received.indexOf("Current status") >= 0) {
    status = currentStatus;
    xstatus = received.substring(15, 19);
    ystatus = received.substring(20, 24);
    dir = received.substring(25, 28);
    dots = false;

    lcd.clear();
    lcd.setCursor(0, 0);
    // lcd.print("Status");
    switch (command) {
      case forward:
        lcd.print("Forward");
        break;
      case backward:
        lcd.print("Backward");
        break;
      case left:
        lcd.print("Left");
        break;
      case right:
        lcd.print("Right");
        break;
      case stop:
        lcd.print("Stop");
        break;
    }
    lcd.setCursor(13, 0);
    lcd.print(dir);
    lcd.setCursor(1, 1);
    lcd.print("x:");
    lcd.print(xstatus);
    lcd.print(", y:");
    lcd.print(ystatus);
  }
  else if (received == "Obstruction found") {
    status = obstruction;
    dots = false;

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Obstruction");
  }

  // Command state handling
  if (received == "Forward") {
    command = forward;
  }
  else if (received == "Backward") {
    command = backward;
  }
  else if (received == "Right") {
    command = right;
  }
  else if (received == "Left") {
    command = left;
  }
  else if (received == "Stop") {
    command = stop;
  }
  else if (received == "Start goal") {
    command = goal;
  }
  else if (received == "Found goal") {
    command = stop;
  }

  received = "";

  // Command state logic
  switch (command) {
    case forward:
      analogWrite(D1, 150);
      digitalWrite(D2, LOW);
      analogWrite(D3, 150);
      digitalWrite(D4, LOW);
      break;
    case backward:
      digitalWrite(D1, LOW);
      analogWrite(D2, 150);
      digitalWrite(D3, LOW);
      analogWrite(D4, 150);
      break;
    case right:
      digitalWrite(D1, HIGH);
      digitalWrite(D2, LOW);
      digitalWrite(D3, LOW);
      digitalWrite(D4, HIGH);
      break;
    case left:
      digitalWrite(D1, LOW);
      digitalWrite(D2, HIGH);
      digitalWrite(D3, HIGH);
      digitalWrite(D4, LOW);
      break;
    case goal:
      // Get TOF sensor reading in front of AGV
      dist = sensor.readRangeSingleMillimeters();

      if (dist < 60) {
        Serial.println("Something in front!");
        command = checkLeft;
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

        i = 0;
      }
      else if (digitalRead(RIR)) {
        delay(50);
        analogWrite(D1, 100);
        digitalWrite(D2, LOW);
        digitalWrite(D3, LOW);
        analogWrite(D4, 150);
        delay(100);
      }
      else if (digitalRead(LIR)) {
        delay(50);
        digitalWrite(D1, LOW);
        analogWrite(D2, 150);
        analogWrite(D3, 100);
        digitalWrite(D4, LOW);
        delay(100);
      }
      else if (digitalRead(FRIR)) {
        delay(50);
        analogWrite(D1, 200);
        digitalWrite(D2, LOW);
        digitalWrite(D3, LOW);
        analogWrite(D4, 255);
        delay(150);
      }
      else if (digitalRead(FLIR)) {
        delay(50);
        digitalWrite(D1, LOW);
        analogWrite(D2, 255);
        analogWrite(D3, 200);
        digitalWrite(D4, LOW);
        delay(150);
      }
      else {
        analogWrite(D1, 50);
        digitalWrite(D2, LOW);
        analogWrite(D3, 50);
        digitalWrite(D4, LOW);
      }
      break;
    case checkRight:
      command = checkLeft;

      if (digitalRead(RIR)) {
        delay(50);
        analogWrite(D1, 150);
        digitalWrite(D2, LOW);
        digitalWrite(D3, LOW);
        analogWrite(D4, 150);
        delay(100);
      }
      else if (digitalRead(LIR)) {
        delay(50);
        digitalWrite(D1, LOW);
        analogWrite(D2, 150);
        analogWrite(D3, 150);
        digitalWrite(D4, LOW);
        delay(100);
      }
      else if (digitalRead(FRIR)) {
        delay(50);
        analogWrite(D1, 255);
        digitalWrite(D2, LOW);
        digitalWrite(D3, LOW);
        analogWrite(D4, 255);
        delay(150);
      }
      else if (digitalRead(FLIR)) {
        delay(50);
        digitalWrite(D1, LOW);
        analogWrite(D2, 255);
        analogWrite(D3, 255);
        digitalWrite(D4, LOW);
        delay(150);
      }
      else {
        analogWrite(D1, 100);
        digitalWrite(D2, LOW);
        digitalWrite(D3, LOW);
        analogWrite(D4, 100);
        delay(100 + i);
        i += 10;
      }

      digitalWrite(D1, LOW);
      digitalWrite(D2, LOW);
      digitalWrite(D3, LOW);
      digitalWrite(D4, LOW);
      delay(200);

      
      break;
    case checkLeft:
      command = checkRight;

      if (digitalRead(RIR)) {
        delay(50);
        analogWrite(D1, 150);
        digitalWrite(D2, LOW);
        digitalWrite(D3, LOW);
        analogWrite(D4, 150);
        delay(100);
      }
      else if (digitalRead(LIR)) {
        delay(50);
        digitalWrite(D1, LOW);
        analogWrite(D2, 150);
        analogWrite(D3, 150);
        digitalWrite(D4, LOW);
        delay(100);
      }
      else if (digitalRead(FRIR)) {
        delay(50);
        analogWrite(D1, 255);
        digitalWrite(D2, LOW);
        digitalWrite(D3, LOW);
        analogWrite(D4, 255);
        delay(150);
      }
      else if (digitalRead(FLIR)) {
        delay(50);
        digitalWrite(D1, LOW);
        analogWrite(D2, 255);
        analogWrite(D3, 255);
        digitalWrite(D4, LOW);
        delay(150);
      }
      else {
        digitalWrite(D1, LOW);
        analogWrite(D2, 100);
        analogWrite(D3, 100);
        digitalWrite(D4, LOW);
        delay(100 + i);
        i += 10;
      }

      digitalWrite(D1, LOW);
      digitalWrite(D2, LOW);
      digitalWrite(D3, LOW);
      digitalWrite(D4, LOW);
      delay(500);
      break;
    default:
      digitalWrite(D1, LOW);
      digitalWrite(D2, LOW);
      digitalWrite(D3, LOW);
      digitalWrite(D4, LOW);
      break;
  }

  // Print dots waiting for next command
  if (dots == true) {
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
    // delay(500);
  }
}
