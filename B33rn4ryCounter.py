#!/usr/bin/python
 
#import
import RPi.GPIO as GPIO
import serial
import time
import datetime
import MySQLdb
import os
 
# Define GPIO mapping
LCD_RS = 25
LCD_E  = 24
LCD_D4 = 23
LCD_D5 = 17
LCD_D6 = 27
LCD_D7 = 22
LCD_LIGHT =  4
VALVE = 7
FLOWSENSOR = 8
 
# Define some device constants
LCD_WIDTH = 20    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
 
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line
 
# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# RFID start and end flags
RFID_START = "\x02"
RFID_END = "\x04"

# Serial bitrate for RFID reader
SERIAL_DEVICE = "/dev/ttyUSB0"
BAUDRATE = 9600

def main():
  # Main program block
 
# Register ISR
  Counter = 0
  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
  GPIO.setup(FLOWSENSOR, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
  def Interrupt(channel):
     global Counter
     Counter = Counter + 1
     print "Counter " + str(Counter)
   
  GPIO.add_event_detect(FLOWSENSOR, GPIO.RISING, callback = Interrupt, bouncetime = 200) 

 
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7
  GPIO.setup(LCD_LIGHT, GPIO.OUT) # Backlight enable
  GPIO.setup(VALVE, GPIO.OUT)
 
  # Initialise display
  lcd_init()

  # Connect to mySQL db
  db = MySQLdb.connect(host="localhost", user="b33rn4ry", passwd="b33rn4ry", db="b33rn4rycounter")
  cursor=db.cursor()

#  lcd_backlight(True)
#  time.sleep(0.5)
#  lcd_string("Uncomressing kernel...",LCD_LINE_1,1)
#  time.sleep(1)
#  lcd_string("Starting ...",LCD_LINE_2,1)
#  time.sleep(1)
#  lcd_string("Starting ...    [OK]",LCD_LINE_2,1)
#  time.sleep(1)
#  lcd_string("B33rn4ry Counter",LCD_LINE_3,1)
#  lcd_string("ready!",LCD_LINE_4,1)
#  time.sleep(3)
#  lcd_backlight(False)
 
  lcd_string("B33rn4ry Counter",LCD_LINE_1,1)
  lcd_string("Idle",LCD_LINE_2,1)
  lcd_string("                    ",LCD_LINE_3,1)
  lcd_string("Waiting for Geeks",LCD_LINE_4,1)

  while True:
    
    # clear variables
    ID = ""
    pID = ""
 
    ID = read_rfid()

    if ID != "":
      if ID != IDtmp:
        pID = str(int(ID[2:], 16))
        lcd_backlight(True)
        lcd_string("Reading RFID tag ...",LCD_LINE_1,1)
        lcd_string("ID:   "+ pID.zfill(10),LCD_LINE_2,1)
        cursor.execute ("SELECT `name` FROM `users` WHERE id = '"+ID+"';")
        result = cursor.fetchone()
        if result is not None:
          lcd_string("User: "+str(result[0]),LCD_LINE_3,1)
          #lcd_string("ACCESS GRANTED!",LCD_LINE_3,1)
          lcd_string("Go ahead and draw a beer!",LCD_LINE_4,1)
          os.system('mpg321 access_granted.mp3 2>&1 > /dev/null &')
          valve(True)
          IDtmp = ID
        else:
          lcd_string("ACCESS DENIED!",LCD_LINE_3,1)
          lcd_string("                    ",LCD_LINE_4,1)
          os.system('mpg321 sadtrombone.mp3')
 
    else:
      valve(False)
      lcd_backlight(False)
      lcd_string("B33rn4ry Counter",LCD_LINE_1,1)
      lcd_string("Idle",LCD_LINE_2,1)
      lcd_string("                    ",LCD_LINE_3,1)
      lcd_string("Waiting for Geeks",LCD_LINE_4,1)
      IDtmp = ""

def read_rfid():
  try:
    ser = serial.Serial(SERIAL_DEVICE, BAUDRATE, timeout=1) 
  except serial.serialutil.SerialException:
    print "Could not open serial device " +SERIAL_DEVICE
  data = ser.read(13)
  ser.close()    
  data = data.replace("R", "" )
  data = data.replace("\x02", "" )
  data = data.replace("\x04", "" )
  return data
 
def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)
 
def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command
 
  GPIO.output(LCD_RS, mode) # RS
 
  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)
 
def lcd_string(message,line,style):
  # Send string to display
  # style=1 Left justified
  # style=2 Centred
  # style=3 Right justified
 
  if style==1:
    message = message.ljust(LCD_WIDTH," ")
  elif style==2:
    message = message.center(LCD_WIDTH," ")
  elif style==3:
    message = message.rjust(LCD_WIDTH," ")
 
  lcd_byte(line, LCD_CMD)
 
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)
 
def lcd_backlight(flag):
  # Toggle backlight on-off-on
  GPIO.output(LCD_LIGHT, flag)

def valve(flag):
  GPIO.output(VALVE, flag)

if __name__ == '__main__':
 
  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Goodbye!",LCD_LINE_1,2)
    GPIO.cleanup()