#include <mcp_can.h>
#include <mcp_can_dfs.h>

#include <mcp_can.h>
#include <SPI.h>

long unsigned int rxId;
unsigned char len = 0;
unsigned char rxBuf[8];
char msgString[128];                        // Array to store serial string

#define CAN0_INT 2                              // Set INT to pin 2
MCP_CAN CAN0(10);                               // Set CS to pin 10

unsigned long currentMillis = 0;


void send_msg(unsigned long id, byte *data, int datalength = 8) {
  byte sndStat = CAN0.sendMsgBuf(id, 1, datalength, data);
  if(sndStat == CAN_OK){
    // Serial.println("Message Sent Successfully!");
  } else {
    Serial.println("Error Sending Message...");
  }
}

void request_battery_customer_code() {
  byte data[8] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
  send_msg(0x02294504, data);
}



void setup()
{
  Serial.begin(115200);

  // Initialize MCP2515 running at 16MHz with a baudrate of 500kb/s and the masks and filters disabled.
  if(CAN0.begin(MCP_ANY, CAN_250KBPS, MCP_8MHZ) == CAN_OK)
    Serial.println("MCP2515 Initialized Successfully!");
  else
    Serial.println("Error Initializing MCP2515...");

  CAN0.setMode(MCP_NORMAL);                     // Set operation mode to normal so the MCP2515 sends acks to received data.

  pinMode(CAN0_INT, INPUT);                            // Configuring pin for /INT input

  Serial.println("MCP2515 Library Receive Example...");

  delay(500);
  //request_battery_customer_code();
}



void loop()
{
  currentMillis = millis();

  checkSerialData();

  if(!digitalRead(CAN0_INT))                         // If CAN0_INT pin is low, read receive buffer
  {
    CAN0.readMsgBuf(&rxId, &len, rxBuf);      // Read data: len = data length, buf = data byte(s)
    if((rxId & 0x04FF3604) == 0x04FF3604){
      return;
    }

    if((rxId & 0x80000000) == 0x80000000)     // Determine if ID is standard (11 bits) or extended (29 bits)
      sprintf(msgString, "Extended ID: 0x%.8lX  DLC: %1d  Data:", (rxId & 0x1FFFFFFF), len);
    else
      sprintf(msgString, "Standard ID: 0x%.3lX       DLC: %1d  Data:", rxId, len);

    Serial.print(msgString);

    if((rxId & 0x40000000) == 0x40000000){    // Determine if message is a remote request frame.
      sprintf(msgString, " REMOTE REQUEST FRAME");
      Serial.print(msgString);
    } else {
      for(byte i = 0; i<len; i++){
        sprintf(msgString, " 0x%.2X", rxBuf[i]);
        Serial.print(msgString);
      }
    }

    Serial.println();
  }
}



const int FRAME_SIZE = 12;  // 4 bytes header + 8 bytes payload
byte header[4];
byte data[8];

int count = 0;
const byte START_BYTE = 0xAA;
bool inFrame = false;

void checkSerialData() {
  // Fill frame buffer with exactly 12 bytes
  while (Serial.available() > 0 && count < FRAME_SIZE) {
    byte b = Serial.read();

    if (!inFrame) {
      // Waiting for start marker
      if (b == START_BYTE) {
        inFrame = true;
        count = 0;
      }
    }
    else {
      if(count < 4){
        header[count] = b;
      } else {
        data[count - 4] = b;
      }
      count++;

      if (count == FRAME_SIZE) {
        processFrame();
        inFrame = false;  // ready for next frame
        count = 0;
      }
    }
  }
}

void processFrame() {
  // need to convert it to long before sending it
  uint32_t headerValue =
    ((uint32_t)header[0] << 24) |
    ((uint32_t)header[1] << 16) |
    ((uint32_t)header[2] << 8)  |
    (uint32_t)header[3];

  send_msg(headerValue, data, 8);


  // // DEBUGGING
  // Serial.print("Header: 0x");
  // for (int i = 0; i < 4; i++) {
  //   if (header[i] < 0x10) Serial.print("0");
  //   Serial.print(header[i], HEX);
  // }

  // Serial.print("  Payload: 0x");
  // for (int i = 0; i < 8; i++) {
  //   if (data[i] < 0x10) Serial.print("0");
  //   Serial.print(data[i], HEX);
  // }

  // Serial.println();
}
