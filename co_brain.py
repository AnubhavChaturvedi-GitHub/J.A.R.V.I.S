from Automation.Automation_Brain import Auto_main_brain,clear_file
from NetHyTechSTT.listen import listen
from TextToSpeech.Fast_DF_TTS import speak
import threading
from Data.DLG_Data import online_dlg,offline_dlg
import random
from Automation.Battery import battery_Alert
from Time_Operations.brain import input_manage,input_manage_Alam
from Features.check_internet_speed import get_internet_speed
from Brain.brain import Main_Brain
from Features.create_file import create_file

numbers = ["1:","2:","3:","4:","5:","6:","7:","8:","9:"]
spl_numbers = ["11:","12:"]

ran_online_dlg = random.choice(online_dlg)
ran_offline_dlg = random.choice(offline_dlg)

def check_inputs():
    output_text = ""
    while True:
        with open("input.txt","r") as file:
            input_text = file.read().lower() 
        if input_text != output_text:
            output_text = input_text
            if output_text.startswith("tell me"):
                output_text = output_text.replace(" p.m.","PM")
                output_text = output_text.replace(" a.m.","AM")
                if "11:" in output_text or "12:" in output_text:
                    input_manage(output_text)
                    clear_file()
                else:
                    for number in numbers:
                        if number in output_text:
                           output_text = output_text.replace(number,f"0{number}")
                           input_manage(output_text)
                           clear_file()
            elif output_text.startswith("set alarm"):
                output_text = output_text.replace(" p.m.","PM")
                output_text = output_text.replace(" a.m.","AM")
                if "11:" in output_text or "12:" in output_text:
                    input_manage_Alam(output_text)
                    clear_file()
                else:
                    for number in numbers:
                        if number in output_text:
                           output_text = output_text.replace(number,f"0{number}")
                           input_manage_Alam(output_text)
                           clear_file()
            elif "check internet speed" in output_text:
                speak("checking your internet speed")
                speed = get_internet_speed()
                speak(f"the device is running on {speed} Mbps internet speed")
            elif "jarvis" in output_text:
                response = Main_Brain(output_text)
                speak(response)
            elif output_text.startswith("create"):
                if "file" in output_text:
                    create_file(output_text)
            else:
                Auto_main_brain(output_text)

def Jarvis():
    clear_file()
    t1 = threading.Thread(target=listen)
    t2 = threading.Thread(target=check_inputs)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
