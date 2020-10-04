"""
'Candy_Factory_Automation.py'
===============================================================================
 
 
Dependencies:
    - Adafruit_Blinka (CircuitPython, on Pi.)
        (https://github.com/adafruit/Adafruit_Blinka)
    - Adafruit_CircuitPython_SGP30.
        (https://github.com/adafruit/Adafruit_CircuitPython_SGP30)
    - Adafruit_CircuitPython_VEML6070.
        (https://github.com/adafruit/Adafruit_CircuitPython_VEML6070)
    - Adafruit_CircuitPython_BME280.
        (https://github.com/adafruit/Adafruit_CircuitPython_BME280)
"""
 
# Import standard python modules
import time

#import stmplib for enabling email notification
import smtplib
 
# import Adafruit Blinka
import board
import busio
 
# import CircuitPython sensor libraries
import adafruit_sgp30
import adafruit_bme280
 
# import Adafruit IO REST client
from Adafruit_IO import Client, Feed, RequestError


import RPi.GPIO as GPIO
GPIO.setmode(GPIO.Board)

#Setting the mode of pin for buzzer and board state
BUZZER= 18
buzzState = False
GPIO.setup(BUZZER, GPIO.OUT)

#Setting the mode of pin for infrared sensor and sensor state

IR_Sensor = 16
GPIO.setup(sensor,GPIO.IN)

#Setting the mode of pin for PIR sensor and sensor state
PIR_PIN = 7
GPIO.setup(PIR_PIN, GPIO.IN)

#Setting the pin for relay which will be used for switching lights
Relay=9
GPIO.setup(Relay, GPIO.OUT)
GPIO.output(Relay, False)




humid=[1,2,3,4,5]  #Adding random values to avoid false alert in the starting 


 
# Adafruit IO key.
ADAFRUIT_IO_KEY = 'YOUR_AIO_KEY'
 
# Adafruit IO username.
ADAFRUIT_IO_USERNAME = 'YOUR_AIO_USERNAME'
 
# Create an instance of the REST client
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
 
try: # if we already have the feeds, assign them.
    tvoc_feed = aio.feeds('tvoc')
    eCO2_feed = aio.feeds('eco2')
    temperature_feed = aio.feeds('temperature')
    humidity_feed = aio.feeds('humidity')
    pressure_feed = aio.feeds('pressure')
    Light_feed=aio.feeds('Light') 
    No_of_units_feed=aio.feeds('Quantity')
    
except RequestError: # if we don't, create and assign them.
    tvoc_feed = aio.create_feed(Feed(name='tvoc'))
    eCO2_feed = aio.create_feed(Feed(name='eco2'))
    Light_feed = aio.create_feed(Feed(name='Light'))
    temperature_feed = aio.create_feed(Feed(name='temperature'))
    humidity_feed = aio.create_feed(Feed(name='humidity'))
    pressure_feed = aio.create_feed(Feed(name='pressure'))
    No_of_units_feed = aio.create_feed(Feed(name='Quantity'))
 
# Create busio I2C
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

# Create BME280 object.
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
bme280.sea_level_pressure = 1013.25
# Create SGP30 object using I2C.
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
sgp30.iaq_init()
sgp30.set_iaq_baseline(0x8973, 0x8aae)


#Email Variables
SMTP_SERVER = 'smtp.gmail.com' #Email Server
SMTP_PORT = 587 #Server Port
GMAIL_USERNAME = 'youremail@email.com' #change this to match your gmail account
GMAIL_PASSWORD = 'yourPassword'  #change this to match your gmail password


#Creating a class for email alert 
class Emailer:
    def sendmail(recipient, subject, content):
         
        #Create Headers
        headers = ["From: " + GMAIL_USERNAME, "Subject: " + subject, "To: " + recipient,
                   "MIME-Version: 1.0", "Content-Type: text/html"]
        headers = "\r\n".join(headers)
 
        #Connect to Gmail Server
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()
 
        #Login to Gmail
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)
 
        #Send Email & Exit
        session.sendmail(GMAIL_USERNAME, recipient, headers + "\r\n\r\n" + content)
        session.quit
#object for class emailer
sender = Emailer()




 

#Creating functions for different sensors with different alert methods

def Air_Quality():
    
     # Read SGP30 sensor
    eCO2_data = sgp30.eCO2
    tvoc_data = sgp30.TVOC
    
    #Adding condition on these paramters for alert with buzzer
    if(tvoc_data>100 or eCO2_data>100):
        #Alert with buzzer that Air quality index is not satisfactory and ventilation system need to be operated at full capacity
            buzzState=True
            GPIO.output(BUZZER, buzzState)
            time.sleep(2)
            buzzState=False
            GPIO.output(BUZZER, buzzState)


    # Send SGP30 Data to Adafruit IO.
    print('eCO2:', eCO2_data)
    aio.send(eCO2_feed.key, eCO2_data)
    print('tvoc:', tvoc_data)
    aio.send(tvoc_feed.key, tvoc_data)
    time.sleep(2)



def THP(): #Here THP stands for Temperature Humidity Pressure
    
    
    # Read BME280 sensor
    temp_data = bme280.temperature
        
    if not (temp_data=>22 and temp_data<=28):
        #Sending an alert that temperature inside the factory is not satisfactory
        #Sending the alert via email
        sendTo = 'anotheremail@email.com'
        emailSubject = "HIGH Temperature level "
        emailContent = "The Temperature level noted to be " + avg + 'Degree celsuis'
        sender.sendmail(sendTo, emailSubject, emailContent)
        print("Email Sent")
        
    
    
    
    #reading the sensor value
    humid_data = bme280.humidity
  
    time.sleep(60) #reading the value at a gap of 1 min
    
    #humid is a list in which values are being appended 
    humid.append(humid_data)
    x=sum(humid[-5:])
    avg=x/5
    
    if(avg>80):
        #Sending the alert via email
        sendTo = 'anotheremail@email.com'
        emailSubject = "Humidity level is more than 80%"
        emailContent = "The Humidity level of last 5 mins is noted to be " + avg + 'Percent'
        sender.sendmail(sendTo, emailSubject, emailContent)
        print("Email Sent")
        
        
    
    
    pressure_data = bme280.pressure
    
    # Send BME280 Data to Adafruit IO.
    print('Temperature: %0.1f C' % temp_data)
    aio.send(temperature_feed.key, temp_data)
    print("Humidity: %0.1f %%" % humid_data)
    aio.send(humidity_feed.key, int(humid_data))
    time.sleep(2)
    print("Pressure: %0.1f hPa" % pressure_data)
    aio.send(pressure_feed.key, int(pressure_data))
  


def No_of_Units():
    

    #Assuming candies are packed in a box which goes to store through conveyor belt
    #We are going to use Infrared sensor to count number of boxes quantity produced in a day
    #We can also add weight sensor to elimate faulty pieces
          if GPIO.input(IR_Sensor):
              print "Object Detected"
              time.sleep(1) #assuming one second time to pass the candy box in front of sensor 
              count=count+1
        
          
        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        
        #Updating the data "total number of boxes" over adafruit platform at the end of day i.e at 11:59pm
        

        if current_time.startswith('23:59'):
            print(current_time)
            Quantity=count
            #Sending the data to adafruit server
            print("No of checked units produced" % Qunatity)
            aio.send(No_of_units_feed.key, int(Quantity))
            time.sleep(60)
            count=0




def Lights():
    
    #Reading PIR sensor value to know the status of lights
    #
    if GPIO.input(PIR_PIN):
        print “Motion Detected!”
        GPIO.output(Relay, True)
        Light=True
        #Sending the data to adafruit server specifically sending the status of the light
        print('Light Status ', Light)
        aio.send(Light_feed.key, Light)
        time.sleep(600) #Turning the lights on for 10 mins
        
    else:    
        GPIO.output(Relay, False)
        Light=False
        #Sending the data to adafruit server specifically sending the status of the light
        print('Light Status ', Light)
        aio.send(Light_feed.key, Light)



while True:
    
    #All the functions will be called here
    Lights()
    No_of_Units()
    THP()
    Air_Quality()
    
    