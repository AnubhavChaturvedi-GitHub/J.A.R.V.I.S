import pywhatkit as kit
import datetime
from TextToSpeech.Fast_DF_TTS import speak
from os import getcwd

now = datetime.datetime.now()
hour = now.hour
minute = now.minute

def clear_file():
    with open(f"{getcwd()}\\input.txt","w") as file:
        file.truncate(0)
        
anubhav = "+919606348280"

def send_msg_wa():
    speak("who do you want to send sir ?")
    output_text = ""
    while True:
        with open("input.txt","r") as file:
            input_text = file.read().lower() 
        if input_text != output_text:
            output_text = input_text
            if output_text.startswith("send to") or output_text.startswith("send tu"):
                output_text.replace("send to","")
                output_text.replace("send tu","")
                if "anubhav" in output_text:
                    speak("By the way what is the message , sir ?")
                    while True:
                       with open("input.txt","r") as file:
                          input_text = file.read().lower() 
                          if input_text != output_text:
                              output_text = input_text
                              if output_text.startswith("message is"):
                                  message =  output_text.replace("message is","")
                                  kit.sendwhatmsg(anubhav,message,hour,minute+1)
                                  speak("message send successfully")
                                 

