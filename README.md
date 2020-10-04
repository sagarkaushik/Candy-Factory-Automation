# Candy-Factory-Automation


Code is written in python which controls the sensors inside the candy factory for safety and better functioning environment of the employees.
Basically, I have used adafruit cloud service.

The parameters which are included in the code for automation are given below:

1) Light
  Using automation energy can be saved by a considerable amount
  Therefore, I tried to automate lights with a PIR sensor which turns on the lights for 10 minutes if the human body is detected by the sensor.
  
2) Temperature and humidity
    Temperature and humidity places crucial role in factory for safety purpose
    Installing sensor which updates the server on real time basis 
    If there are any abnormal conditions an email alert will be sent to the employee.
    
 
3) Air quality
    AQI (Air Quality Index) must be good for good health care of staff working in the factory.
    AQI sensors can be used to keep the server updated on real time basis 
    Alert is raised if the AQI is moderate or worst with the help of buzzer which indicates ventilation should be started at full capacity
    
    
4) No of units 
    A company always wants to keep a check on the number of quantities or units being produced in a day.
    I have used IR sensor to detect the boxes over conveyor belt and this data will be updated at the end of the day(11:59 pm) to the server
    


