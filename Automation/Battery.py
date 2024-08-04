# pip install psutil
# CTRL + J Terminal 

import psutil
import time
import time
from TextToSpeech.Fast_DF_TTS import speak
import threading
from Alert import Alert

battery = psutil.sensors_battery()

def battery_Alert():
    while True:
        time.sleep(3)
        percentage = int(battery.percent)
        if percentage == 100:
            t1 = threading.Thread(target=Alert,args=("100%charge",))
            t2 = threading.Thread(target=speak,args=("100% charged. Please unplug it.",))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        elif percentage <= 20:
            t1 = threading.Thread(target=Alert,args=("Battery Low",))
            t2 = threading.Thread(target=speak,args=("Sir,Sorry to disturb you but battery is Low now",))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        elif percentage <=10:
            t1 = threading.Thread(target=Alert,args=("Battery is too Low",))
            t2 = threading.Thread(target=speak,args=("Sir,Sorry to disturb you but we are running on very low battery power",))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        elif percentage <= 5:
            t1 = threading.Thread(target=Alert,args=("Battery is going to died",))
            t2 = threading.Thread(target=speak,args=("Sir,Sorry to disturb you but this is your last chance sir , charge your system now",))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        time.sleep(10)




def check_plug():
    print("_____started___")
    battery = psutil.sensors_battery()
    previous_state = battery.power_plugged
    while True:
        battery = psutil.sensors_battery()
        if battery.power_plugged != previous_state:
            if battery.power_plugged:
                t1 = threading.Thread(target=Alert,args=("Charging **STARTED**",))
                t2 = threading.Thread(target=speak,args=("Charging Started",))
                t1.start()
                t2.start()
                t1.join()
                t2.join()
            else:
                t1 = threading.Thread(target=Alert,args=("Charging **STOP**",))
                t2 = threading.Thread(target=speak,args=("Charging Stop",))
                t1.start()
                t2.start()
                t1.join()
                t2.join()
      
            previous_state = battery.power_plugged



def check_percentage():
    battery = psutil.sensors_battery()
    percent = int(battery.percent)
    t1 = threading.Thread(target=Alert,args=(f"The device is running on {percent}% power",))
    t2 = threading.Thread(target=speak,args=(f"The device is running on {percent}% power",))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    

