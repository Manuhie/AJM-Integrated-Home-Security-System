// Include Arduino Wire library for I2C
#include <Wire.h>
// Include LCD display library for I2C
#include <LiquidCrystal_I2C.h>
// Include Keypad library
#include <Keypad.h>
 
// Length of password + 1 for null character
#define Password_Length 8
// Character to hold password input
char Data[Password_Length];
// Password
char Master[Password_Length] = "123A456";
char Emergency[Password_Length] = "123B456";
 
// Pin connected to lock relay input
int lockOutput = 13;
 
// Counter for character entries
byte data_count = 0;
 
// Character to hold key input
char customKey;
 
// Constants for row and column sizes
const byte ROWS = 4;
const byte COLS = 4;
 
// Array to represent keys on keypad
char hexaKeys[ROWS][COLS] = {
  {'1', '4', '7', '*'},
  {'2', '5', '8', '0'},
  {'3', '6', '9', '#'},
  {'A', 'B', 'C', 'D'}
};
 
// Connections to Arduino
byte rowPins[ROWS] = {9, 8, 7, 6};
byte colPins[COLS] = {5, 4, 3, 2};
 
// Create keypad object
Keypad customKeypad = Keypad(makeKeymap(hexaKeys), rowPins, colPins, ROWS, COLS);
 
// Create LCD object
LiquidCrystal_I2C lcd(0x27, 16, 2);
 
void setup() {
  // put your setup code here, to run once:
Serial.begin(19200);
Serial.setTimeout(0.1);

  lcd.init();
 
  // Set lockOutput as an OUTPUT pin
  pinMode(lockOutput, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
if (Serial.available() >0){
     String msg = Serial.readString();
    if (msg == "CHECK"){
      askPass();
    }else if (msg == "OPEN"){
      openDoor();
    }
  }
}
void askPass(){
  lcd.backlight();
  bool code = true;
  while(code){
   // Initialize LCD and print
  lcd.setCursor(0, 0);
  lcd.print("Enter Password:");
 
  // Look for keypress
  customKey = customKeypad.getKey();
  if (customKey) {
    // Enter keypress into array and increment counter
    Data[data_count] = customKey;
    lcd.setCursor(data_count, 1);
    lcd.print("*");
    data_count++;
  }
 
  // See if we have reached the password length
  if (data_count == Password_Length - 1) {
    lcd.clear();
 
    if (!strcmp(Data, Master)) {
      // Password is correct
      lcd.print("Correct");
      // Turn on relay for 5 seconds
      digitalWrite(lockOutput, HIGH);
      code = false;
      Serial.write("OK");
      delay(5000);
      digitalWrite(lockOutput, LOW);
    }
    else if(!strcmp(Data, Emergency)) {
      // Password is correct
      emerg();
      code = false;
      lcd.print("Correct");
      // Turn on relay for 5 seconds
      digitalWrite(lockOutput, HIGH);
      delay(5000);
      digitalWrite(lockOutput, LOW);}
    else {
      // Password is incorrect
      lcd.print("Incorrect");
      delay(1000);
    }
 
    // Clear data and LCD display
    lcd.clear();
    clearData();
  }
}lcd.noBacklight();
}
void clearData() {
  // Go through array and clear data
  while (data_count != 0) {
    Data[data_count--] = 0;
  }
}
void emerg(){
  Serial.write("EMERG");
}
void openDoor(){
   lcd.backlight();
   lcd.setCursor(0, 0);
   lcd.print("You can proceed!");
   digitalWrite(lockOutput, HIGH);
   delay(5000);
   digitalWrite(lockOutput, LOW);
   lcd.clear();
   clearData();
   lcd.noBacklight();
}
