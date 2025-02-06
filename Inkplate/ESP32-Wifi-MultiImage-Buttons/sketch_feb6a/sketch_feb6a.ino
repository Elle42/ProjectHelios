#include <WiFi.h>
#include "Inkplate.h"

const char* ssid = "ESP32_Network";
const char* password = "123456789";

IPAddress localIP(192, 168, 0, 254);
IPAddress subnet(255, 255, 255, 0);

WiFiServer tcpServer(3333);
Inkplate display;

const int buttonPin1 = 26;
const int buttonPin2 = 36;

bool lastState1 = LOW;
bool lastState2 = LOW;

int imageIndex = 0;
int totalImages = 0;

void setup() {
    Serial.begin(115200);
    WiFi.softAPConfig(localIP, localIP, subnet);
    WiFi.softAP(ssid, password);
    Serial.println("Access Point IP: " + WiFi.softAPIP().toString());

    tcpServer.begin();
    Serial.println("Server gestartet");

    display.begin();
    display.display();
    display.sdCardInit();

    pinMode(buttonPin1, INPUT_PULLUP);
    pinMode(buttonPin2, INPUT_PULLUP);

    if (totalImages > 0) {
        showImage(0); // Erstes Bild anzeigen, falls vorhanden
    }
}

void loop() {
    bool currentState1 = digitalRead(buttonPin1);
    bool currentState2 = digitalRead(buttonPin2);

    if (lastState1 == LOW && currentState1 == HIGH) {
        if (totalImages > 0) {
            Serial.println("Button 1 gedrückt - Nächstes Bild");
            imageIndex = (imageIndex + 1) % totalImages;
            showImage(imageIndex);
        } else {
            Serial.println("Keine Bilder vorhanden!");
        }
        delay(200);
    }
    if (lastState2 == LOW && currentState2 == HIGH) {
        if (totalImages > 0) {
            Serial.println("Button 2 gedrückt - Vorheriges Bild");
            imageIndex = (imageIndex - 1 + totalImages) % totalImages;
            showImage(imageIndex);
        } else {
            Serial.println("Keine Bilder vorhanden!");
        }
        delay(200);
    }
    lastState1 = currentState1;
    lastState2 = currentState2;

    WiFiClient client = tcpServer.available();
    if (client) {
        Serial.println("Client verbunden");

        char fileName[20];
        snprintf(fileName, sizeof(fileName), "/image%d.bmp", totalImages);

        File imageFile;
        imageFile.open(fileName, FILE_WRITE);
        if (!imageFile) {
            Serial.println("Datei konnte nicht erstellt werden.");
            return;
        }

        while (client.connected()) {
            if (client.available()) {
                uint8_t buffer[5096];
                int bytesRead = client.read(buffer, sizeof(buffer));
                if (bytesRead > 0) {
                    imageFile.write(buffer, bytesRead);
                    Serial.printf("Empfangen: %d Bytes\n", bytesRead);
                }
            }
        }
        imageFile.close();
        Serial.println("Datei gespeichert");

        totalImages++;
        if (totalImages == 1) {
            showImage(0);
        }
    }
}

void showImage(int index) {
    if (totalImages == 0) {
        Serial.println("Keine Bilder zum Anzeigen!");
        return;
    }

    char fileName[20];
    snprintf(fileName, sizeof(fileName), "/image%d.bmp", index);
    display.clearDisplay();
    if (display.drawBitmapFromSd(fileName, 1, 1, 0, 0)) {
        display.display();
        Serial.printf("Bild %d angezeigt\n", index);
    } else {
        Serial.println("Fehler beim Laden des Bildes");
    }
}
