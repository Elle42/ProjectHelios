#include <ArduinoBLE.h>

// Definiere den LED-Pin (Pin 2 ist bei vielen ESP32-Boards die integrierte LED)
const int ledPin = 2;

// UUIDs für den BLE-Service und die Characteristics
#define SERVICE_UUID        "0000ffb0-0000-1000-8000-00805f9b34fb"
#define CHARACTERISTIC_UUID "0000ffb1-0000-1000-8000-00805f9b34fb"

// BLE-Service und Characteristic-Objekte
BLEService ledService(SERVICE_UUID);
BLECharacteristic ledCharacteristic(CHARACTERISTIC_UUID, BLEWrite, 20);

void setup() {
  // Initialisierung der seriellen Kommunikation
  Serial.begin(9600);
  
  // LED-Pin als Ausgang festlegen
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);  // LED zunächst ausschalten

  // BLE initialisieren
  if (!BLE.begin()) {
    Serial.println("Starting BLE failed!");
    while (1);
  }

  // BLE-Gerät initialisieren
  BLE.setLocalName("ESP32_LED_Control");   // Setzt den Gerätenamen
  BLE.setAdvertisedService(ledService);    // Stellt den Service bereit

  // Füge die Characteristics zum Service hinzu
  ledService.addCharacteristic(ledCharacteristic);

  // Start des Services
  BLE.addService(ledService);

  // Startet das Advertising, um Verbindungen zu ermöglichen
  BLE.advertise();
  
  Serial.println("BLE device is now advertising, waiting for a connection...");
}

void loop() {
  // Client verbinden
  BLEDevice central = BLE.central();

  // Wenn ein zentraler Client verbunden ist
  if (central) {
    Serial.print("Connected to central: ");
    Serial.println(central.address());

    // Solange der zentrale Client verbunden ist
    while (central.connected()) {
      // Prüfe, ob Daten auf der Characteristic geschrieben wurden
      if (ledCharacteristic.written()) {
        // Wert als uint8_t* erhalten und in einen String umwandeln
        String receivedValue = "";
        for (int i = 0; i < ledCharacteristic.valueLength(); i++) {
          receivedValue += (char)ledCharacteristic.value()[i];
        }

        Serial.print("Received Value: ");
        Serial.println(receivedValue);

        // Prüfe, ob der Wert "ON" oder "OFF" ist
        if (receivedValue == "ON") {
          digitalWrite(ledPin, HIGH);  // Schaltet die LED ein
        } else if (receivedValue == "OFF") {
          digitalWrite(ledPin, LOW);   // Schaltet die LED aus
        }
      }
    }

    // Wenn der zentrale Client die Verbindung trennt
    Serial.print("Disconnected from central: ");
    Serial.println(central.address());
  }
}
