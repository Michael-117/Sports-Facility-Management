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
const char* ssid = "PearFi-2";
const char* password = "P3arsonHousehold";
const char* serverName = "http://192.168.0.4/SFMS/verify";

//POST Request Information
String sensor = "SensorA";
String facilityID = "1";
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
String masterOffID = "347EFD29";
byte readCard[4];
boolean successRead, correctTag, masterState= false;

//Timer Variables
volatile int interruptCounter;
int interruptCounter0;
int interruptCounter1;
hw_timer_t * timer0 = NULL;
hw_timer_t * timer1 = NULL;
portMUX_TYPE timerMux0 = portMUX_INITIALIZER_UNLOCKED;
portMUX_TYPE timerMux1 = portMUX_INITIALIZER_UNLOCKED;


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
  message = "";
  tagID = "";
  readRFID();
  if (message != ""){
    post(message);
  }
  if (grant == 2){
    masterOn();
  }
  if (grant == 3){
    masterOff();
  }
  
  if (grant != 0 && grant != 2 && grant != 3){
  
    resourceOn(resourceID);
    lcd.setCursor(0,2);
    lcd.print("                    ");
    lcd.setCursor(0,2);
    lcd.print("READ ID: ");
    lcd.setCursor(9, 2);
    lcd.print(tagID);
      
    if (resourceID == 1){
      lcd.setCursor(0, 3);
      lcd.print("Resource 1 Turned On");
    }
    if (resourceID == 2){
      lcd.setCursor(0, 3);
      lcd.print("Resource 2 Turned On");
    }

    delay(5000);
    resourceOff(resourceID);
    lcd.setCursor(0, 2);
    lcd.print("                    ");
    lcd.setCursor(0, 2);
    lcd.print("PLEASE SWIPE ID CARD");
    lcd.setCursor(0,3);
    lcd.print("                    ");
  }
  if (grant == 0 && tagID != ""){
    lcd.setCursor(0,2);
    lcd.print("                    ");
    lcd.setCursor(0,2);
    lcd.print("READ ID: ");
    lcd.setCursor(9, 2);
    lcd.print(tagID);
    lcd.setCursor(0, 3);
    lcd.print("Access Denied");
    delay(3000);
    lcd.setCursor(0, 2);
    lcd.print("PLEASE SWIPE ID CARD");
    lcd.setCursor(0,3);
    lcd.print("                    ");
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

//Timer Code
void IRAM_ATTR onTimer0(){
  portENTER_CRITICAL_ISR(&timerMux0);
  interruptCounter0++;
  portEXIT_CRITICAL_ISR(&timerMux0);
}

void IRAM_ATTR onTimer1(){
  portENTER_CRITICAL_ISR(&timerMux1);
  interruptCounter1++;
  portEXIT_CRITICAL_ISR(&timerMux1);
}

void relay1_Timer(){
  timer0 = timerBegin(0, 80, true);
  timerAttachInterrupt(timer0, &onTimer0, true);
  timerAlarmWrite(timer0, 1000000, true);
  yield();
  timerAlarmEnable(timer0);
}

void relay2_Timer(){
  timer1 = timerBegin(1, 80, true);
  timerAttachInterrupt(timer1, &onTimer1, true);
  timerAlarmWrite(timer1, 1000000, true);
  yield();
  timerAlarmEnable(timer1);
}

void stopRelay1_Timer(int endTime1){
  if (interruptCounter0 == endTime1){
    timerAlarmDisable(timer0);
    timerDetachInterrupt(timer0);
    timerEnd(timer0);
    timer0 = NULL;
    interruptCounter0 = 0;
  }
}

void stopRelay2_Timer(int endTime2){
  if (interruptCounter1 == endTime2){
    timerAlarmDisable(timer1);
    timerDetachInterrupt(timer1);
    timerEnd(timer1);
    timer1 = NULL;
    interruptCounter1 = 0;
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
  }
  if (resourceID == 2){
    digitalWrite(relay2, HIGH);
  }
  grant = 0;
}

void masterOn(){
  digitalWrite(relay1, LOW);
  digitalWrite(relay2, LOW);
}

void masterOff(){
  digitalWrite(relay1, HIGH);
  digitalWrite(relay2, HIGH);
}

//HTTP Code
void connectToNetwork(){
  
  WiFi.begin(ssid, password);
 
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Establishing connection to WiFi..");
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
    
    //Integer Values for permission, resourceID and time
    grant = stateString.toInt();
    if (tagID == masterOnID){
      grant = 2;
    }
    if (tagID == masterOffID){
      grant = 3;
    }
    resourceID = resourceIDString.toInt();
    endTime = endTimeVar.toInt();
    http.end();
  }
  else{
    Serial.println("Wi-Fi Disconnected");
  }
}
