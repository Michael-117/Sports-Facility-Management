//Libraries//
#include <SPI.h>                //Serial Peripheral Interface
#include <MFRC522.h>            //Radio Frequency Identification 
#include <WiFi.h>               //Wi-Fi Functionality
#include <HTTPClient.h>         //HTTP Client Library
#include <LiquidCrystal_I2C.h>  //Liquid Crystal Display library for I2C

//Microcontroller Pin Definitions
#define RST_PIN 22              //Serial Clock Line
#define SS_PIN 21               //Serial Select Line
#define redLED 15               //Red LED
#define yellowLED 0             //Yellow LED
#define blueLED 4               //Blue LED
#define relay1 33               //Relay #1
#define relay2 32               //Relay #2

//Wi-Fi Setup Constants
const char* ssid = "SSID";
const char* password = "PASSWORD";
const char* serverName = "http://192.168.0.4/SFMS/verify";

//POST Request Information
String sensor = "SensorB";
String facilityID = "2";
int resourceID, grant, endTime;

//HTTP Variables
String message;
String httpResponse;

//Instance Creation
WiFiClient client;
HTTPClient http;
MFRC522 rfid(SS_PIN, RST_PIN);
LiquidCrystal_I2C lcd(0x27, 20, 4);

//RFID Variables
String tagID = "";
String masterOnID = "5A797D7F";
String masterOffID = "9C52B";
byte readCard[4];

//Timer Variables
volatile int interruptCounter0;
volatile int interruptCounter1;
int totalInterruptCounter0;
int totalInterruptCounter1;
hw_timer_t * timer0 = NULL;
hw_timer_t * timer1 = NULL;
portMUX_TYPE timerMux0 = portMUX_INITIALIZER_UNLOCKED;
portMUX_TYPE timerMux1 = portMUX_INITIALIZER_UNLOCKED;
unsigned long now1, now2, past1, past2, onTime1, onTime2 = 0;

int opMode = 0;

void setup() {
  pinMode(redLED, OUTPUT);
  pinMode(yellowLED, OUTPUT);
  pinMode(blueLED, OUTPUT);
  pinMode(relay1, OUTPUT);
  pinMode(relay2, OUTPUT);
  digitalWrite(relay1, HIGH);
  digitalWrite(relay2, HIGH);
  Serial.begin(115200);
  SPI.begin();
  Wire.begin(26,25);
  rfid.PCD_Init();
  lcd.init();
  lcd.backlight();
  lcd.setCursor(2, 0);
  lcd.print("SPORTS  FACILITY");
  lcd.setCursor(1, 1);
  lcd.print("MANAGEMENT  SYSTEM");
  lcd.setCursor(0, 2);
  lcd.print("PLEASE SWIPE ID CARD");
  connectToNetwork();
}

void loop() {

  if (opMode != 9){
    countdown1(onTime1);
    countdown2(onTime2);
  }  
  message = "";
  tagID = "";
  readRFID();
  if (message != ""){
    post(message);
  }
  
}

void countdown1(int onTime1){
  now1 = millis();
  Serial.print("Now 1: ");
  Serial.println(now1);
  Serial.print("Countdown 1: ");
  Serial.println(onTime1);
  if((now1 > onTime1) && (digitalRead(relay1) == LOW)){
    digitalWrite(relay1,HIGH);
  }
}

void countdown2(int onTime2){
  now2 = millis();
  Serial.print("Now 2: ");
  Serial.println(now2);
  Serial.print("Countdown 2: ");
  Serial.println(onTime2);
  if((now2 > onTime2) && (digitalRead(relay2) == LOW)){
    digitalWrite(relay2,HIGH);
  }
}
  
void readRFID(){
  if ( ! rfid.PICC_IsNewCardPresent()) { //If a new PICC placed to RFID reader continue
    return;
  }
  if ( ! rfid.PICC_ReadCardSerial()) {   //Since a PICC placed get Serial and continue
    return;
  }
  else{
    tagID = "";
    for ( uint8_t i = 0; i < 4; i++) {  // The MIFARE PICCs that we use have 4 byte UID
      readCard[i] = rfid.uid.uidByte[i];
      tagID.concat(String(rfid.uid.uidByte[i], HEX)); // Adds the 4 bytes in a single String variable
    }
    tagID.toUpperCase();
    rfid.PICC_HaltA(); // Stop 
    Serial.print("Tag ID Read = ");
    Serial.println(tagID);
    message = "sensor=" + sensor + "&facilityID=" + facilityID + "&rfid=" + (String)tagID;
  }
}

//Control Resources
void resourceOn(int resourceID){
  if (resourceID == 1){
    digitalWrite(relay1, LOW);
  }
  if (resourceID == 2){
    digitalWrite(relay2, LOW);
  }
}

void resourceOff(int resourceID){
  if (resourceID == 1){
    digitalWrite(relay1, HIGH);
    onTime1 = 0;
  }
  if (resourceID == 2){
    digitalWrite(relay2, HIGH);
    onTime2 = 0;
  }
}

void masterOn(){
  opMode = 9;
  digitalWrite(relay1, LOW);
  digitalWrite(relay2, LOW);
  onTime1 = 0;
  onTime2 = 0;
  now1 = 0;
  now2 = 0;
  lcd.setCursor(0,3);
  lcd.print("                    ");
  lcd.setCursor(0,3);
  lcd.print("     MASTER  ON     ");
}

void masterOff(){
  digitalWrite(relay1, HIGH);
  digitalWrite(relay2, HIGH);
  onTime1 = 0;
  onTime2 = 0;
  lcd.setCursor(0,3);
  lcd.print("                    ");
  opMode = 0;
}

//HTTP Code
void connectToNetwork(){
  
  WiFi.begin(ssid, password);
  int tryCount = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Establishing connection to WiFi..");
    tryCount++;
    if (tryCount == 5){
      ESP.restart();
    }
  }
 
  Serial.print("Connected to network: ");
  Serial.print(ssid);
  Serial.print(" with IP address: ");
  Serial.println(WiFi.localIP());
 
}

void post(String message){
  
  if (WiFi.status() == WL_CONNECTED){
    http.begin(serverName);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    Serial.print("Message being sent in POST: ");
    Serial.println(message);
    http.POST(message);
    httpResponse = http.getString();
    const char* responseString = httpResponse.c_str();

    //Access granted or denied
    char state = responseString[0];
    String stateString = (String)state;

    //Resource to control
    char resource__ID = responseString[2];
    String resourceIDString = (String)resource__ID;

    //Time for use
    String endTimeVar = httpResponse.substring(4);
    String testVar = stateString + "," + resourceIDString + "," + endTimeVar;
    Serial.println(testVar);

    endTime = endTimeVar.toInt() * 1000;
    
    //Integer Values for permission, resourceID and time
    if ((stateString == "1")&&(resourceIDString == "3")){
      masterOn();
    }
    if ((stateString == "0")&&(resourceIDString == "3")){
      masterOff();
    }
    if ((stateString == "1")&&(resourceIDString == "1")){
      onTime1 = now1 + endTime;
      resourceOn(1);
      countdown1(onTime1);
      lcd.setCursor(0,2);
      lcd.print("                    ");
      lcd.setCursor(0,2);
      lcd.print("CARD READ: ");
      lcd.setCursor(10,2);
      lcd.print(tagID);
      lcd.setCursor(0,3);
      lcd.print("  ACCESS GRANTED  ");
      delay(5000);
      lcd.setCursor(0,2);
      lcd.print("                    ");
      lcd.setCursor(0,2);
      lcd.print("PLEASE SWIPE ID CARD");
      lcd.setCursor(0,3);
      lcd.print("                    ");
    }
    if ((stateString == "1")&&(resourceIDString == "2")){
      onTime2 = now2 + endTime - 5000;
      resourceOn(2);
      countdown2(onTime2);
      lcd.setCursor(0,2);
      lcd.print("                    ");
      lcd.setCursor(0,2);
      lcd.print("CARD READ: ");
      lcd.setCursor(10,2);
      lcd.print(tagID);
      lcd.setCursor(0,3);
      lcd.print("  ACCESS GRANTED  ");
      delay(5000);
      lcd.setCursor(0,2);
      lcd.print("                    ");
      lcd.setCursor(0,2);
      lcd.print("PLEASE SWIPE ID CARD");
      lcd.setCursor(0,3);
      lcd.print("                    ");
    }
    if ((stateString == "0")&&(resourceIDString == "N")){
      lcd.setCursor(0,2);
      lcd.print("                    ");
      lcd.setCursor(0,2);
      lcd.print("  CARD READ: ");
      lcd.setCursor(10,2);
      lcd.print(tagID);
      lcd.setCursor(0,3);
      lcd.print("  ACCESS Denied  ");
      delay(4000);
      lcd.setCursor(0,2);
      lcd.print("                    ");
      lcd.setCursor(0,3);
      lcd.print("                    ");
      lcd.setCursor(0,2);
      lcd.print("  NO BOOKING FOUND  ");
      lcd.setCursor(0,3);
      lcd.print(" CONTACT MANAGEMENT ");
      delay(4000);
      lcd.setCursor(0,2);
      lcd.print("                    ");
      lcd.setCursor(0,3);
      lcd.print("                    ");
      lcd.setCursor(0,2);
      lcd.print("PLEASE SWIPE ID CARD");
    }
    http.end();
  }
  else{
    Serial.println("Wi-Fi Disconnected");
  }
}
