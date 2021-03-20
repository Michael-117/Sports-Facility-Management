
#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <LiquidCrystal_I2C.h>

#define RST_PIN 22
#define SS_PIN 21
#define redLED 15
#define yellowLED 0
#define blueLED 4
#define relay1 33
#define relay2 32

// Define LCD variables

int lcdColumns = 20;
int lcdRows = 4;

// Define WiFi variables
const char* ssid = "PearFi-2";
const char* password = "P3arsonHousehold";
const char* serverName = "http://192.168.0.4/comp3901/verifyBooking.php";
String sensorName = "SensorA";
String sensorLocation = "SCourt";
String message;
int httpResponse;

WiFiClient client;

HTTPClient http;

MFRC522 rfid(SS_PIN, RST_PIN);  // Create MFRC522 instance

LiquidCrystal_I2C lcd(0x27, lcdColumns, lcdRows);

byte readCard[4];
String masterID = "5A797D7F";
String expectedID1 = "245DC29";
String expectedID2 = "348212A";
String tagID = "";
String lastID = "";
boolean successRead = false;
boolean correctTag = false;


void setup() {
  pinMode(redLED, OUTPUT);
  pinMode(yellowLED, OUTPUT);
  pinMode(blueLED, OUTPUT);
  pinMode(relay1, OUTPUT);
  pinMode(relay2, OUTPUT);
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
  digitalWrite(redLED,HIGH);
  digitalWrite(yellowLED, LOW);
  digitalWrite(blueLED, LOW);
  //digitalWrite(relay1, HIGH);
  //digitalWrite(relay2, HIGH);     

  if ( ! rfid.PICC_IsNewCardPresent()) { //If a new PICC placed to RFID reader continue
    return;
  }
  if ( ! rfid.PICC_ReadCardSerial()) {   //Since a PICC placed get Serial and continue
    return;
  }
  else{
    digitalWrite(redLED,LOW);
    digitalWrite(yellowLED, HIGH);

    lcd.setCursor(0, 2);
    lcd.print("                    ");
    lcd.setCursor(0, 2);
    lcd.print("     READING ID...  "); 

    lastID = tagID;
    tagID = "";
    for ( uint8_t i = 0; i < 4; i++) {  // The MIFARE PICCs that we use have 4 byte UID
      readCard[i] = rfid.uid.uidByte[i];
      tagID.concat(String(rfid.uid.uidByte[i], HEX)); // Adds the 4 bytes in a single String variable
    }
    tagID.toUpperCase();
    rfid.PICC_HaltA(); // Stop reading
    Serial.print("Tag ID Read = ");
    Serial.println(tagID);
    delay(2000);

    
    if ( tagID == masterID && lastID != masterID){
      digitalWrite(yellowLED, LOW);
      digitalWrite(blueLED, HIGH);
      digitalWrite(relay1, LOW);
      digitalWrite(relay2, LOW);
      
      lcd.setCursor(0, 2);
      lcd.print("                    ");
      lcd.setCursor(0, 2);
      lcd.print("READ ID: ");
      lcd.setCursor(9, 2);
      lcd.print("MASTER CARD");
      lcd.setCursor(0, 3);
      lcd.print("Court Lights On");
      delay(5000);
      lcd.setCursor(0, 2);
      lcd.print("                    ");
      lcd.setCursor(0, 3);
      lcd.print("                    ");
      lcd.setCursor(0, 2);
      lcd.print("PLEASE SWIPE ID CARD");
    }
    
    if ( tagID == masterID && lastID == masterID){
      digitalWrite(yellowLED, LOW);
      digitalWrite(blueLED, HIGH);
      digitalWrite(relay1, HIGH);
      digitalWrite(relay2, HIGH);
      
      lcd.setCursor(0, 2);
      lcd.print("                    ");
      lcd.setCursor(0, 2);
      lcd.print("READ ID: ");
      lcd.setCursor(9, 2);
      lcd.print("MASTER CARD");
      lcd.setCursor(0, 3);
      lcd.print("Court Lights Off");
      delay(5000);
      lcd.setCursor(0, 2);
      lcd.print("                    ");
      lcd.setCursor(0, 3);
      lcd.print("                    ");
      lcd.setCursor(0, 2);
      lcd.print("PLEASE SWIPE ID CARD");
    }
    
    if (tagID == expectedID1){
      digitalWrite(yellowLED, LOW);
      digitalWrite(blueLED, HIGH);
      digitalWrite(relay1, LOW);
      message = "sensor=" + (String)sensorName + "&location=" + (String)sensorLocation + "&rfid=" + (String)tagID;
      post(message);
      message = "";
      
      lcd.setCursor(0, 2);
      lcd.print("                    ");
      lcd.setCursor(0, 2);
      lcd.print("READ ID: ");
      lcd.setCursor(9, 2);
      lcd.print(tagID);
      lcd.setCursor(0, 3);
      lcd.print("Court 1 Lights On");
      delay(5000);
      lcd.setCursor(0, 2);
      lcd.print("                    ");
      lcd.setCursor(0, 3);
      lcd.print("                    ");
      lcd.setCursor(0, 2);
      lcd.print("PLEASE SWIPE ID CARD");
    }
    
    if (tagID == expectedID2){
      digitalWrite(yellowLED, LOW);
      digitalWrite(blueLED, HIGH);
      digitalWrite(relay2, LOW);
      message = "sensor=" + (String)sensorName + "&location=" + (String)sensorLocation + "&rfid=" + (String)tagID;
      post(message);
      message = "";
      lcd.setCursor(0, 2);
      lcd.print("                    ");
      lcd.setCursor(0, 2);
      lcd.print("READ ID: ");
      lcd.setCursor(9, 2);
      lcd.print(tagID);
      lcd.setCursor(0, 3);
      lcd.print("Court 2 Lights On");
      delay(5000);
      lcd.setCursor(0, 2);
      lcd.print("                    ");
      lcd.setCursor(0, 3);
      lcd.print("                    ");
      lcd.setCursor(0, 2);
      lcd.print("PLEASE SWIPE ID CARD");
    }
    else{
      return;
    }
  }
}


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
    httpResponse = http.POST(message);

    if(httpResponse > 0){
      Serial.print("HTTP Response Code: ");
      Serial.println(httpResponse);
    }
    else{
      Serial.print("HTTP Error Code: ");
      Serial.println(httpResponse);
    }
    http.end();
  }
  else{
    Serial.println("Wi-Fi Disconnected");
  }
}
