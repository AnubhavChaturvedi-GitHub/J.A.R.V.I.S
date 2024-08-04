from Automation.open_App import open_App
from Automation.Web_Open import openweb
import pyautogui as gui
from Automation.Play_Music_YT import play_music_on_youtube
from TextToSpeech import Fast_DF_TTS
from Automation.playmusic_Sfy import play_music_on_spotify
from Automation.Battery import check_percentage
from os import getcwd
import time
from Automation.tab_automation import perform_browser_action
from Automation.Youtube_play_back import perform_media_action
import pywhatkit
from Automation.scrool_system import perform_scroll_action
import threading
from TextToSpeech.Fast_DF_TTS import speak

def play():
    gui.press("space")
    
def search_google(text):
    pywhatkit.search(text)

def close():
    gui.hotkey('alt','f4')
    
def search(text):
    gui.press("/")
    time.sleep(0.3)
    gui.write(text)

def Open_Brain(text):
    if "website" in text or "open website named" in text:
        text = text.replace("open","").strip()
        text = text.replace("website","").strip()
        text = text.replace("open website named","").strip()
        t1 = threading.Thread(target=speak,args=(f"Navigating {text} website",))
        t2 = threading.Thread(target=openweb,args=(text,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    else:
        text = text.replace("open","").strip()
        text = text.replace("app","").strip()
        t1 = threading.Thread(target=speak,args=(f"Navigating {text} application",))
        t2 = threading.Thread(target=open_App,args=(text,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
def clear_file():
    with open(f"{getcwd()}\\input.txt","w") as file:
        file.truncate(0)

def Auto_main_brain(text):
   try: 
    if text.startswith("open"):
        Open_Brain(text)
    elif "close" in text:
        close()
    elif "play music" in text or "play music on youtube" in text:
        Fast_DF_TTS.speak("which song do you want to play sir.")
        clear_file()
        output_text = ""
        while True:
            with open("input.txt","r") as file:
                input_text = file.read().lower()
            if input_text != output_text:
                output_text = input_text
                if output_text.endswith("song"):
                    play_music_on_youtube(output_text)
                    break
                    
        else:
            pass
        
    elif "play some music" in text or "play music on spotify" in text:
        Fast_DF_TTS.speak("Which song do you want to play, sir.")
        clear_file()
        output_text = ""
        while True:
            with open("input.txt", "r") as file:
                input_text = file.read().lower()
            if input_text != output_text:
                output_text = input_text
                if output_text.endswith("song"):
                    play_music_on_spotify(output_text)
                    break

    elif "check battery percentage" in text or "check battery level" in text:
        check_percentage()
    elif text.startswith("search"):
        text = text.replace("search","")
        text = text.strip()
        t1 = threading.Thread(target=speak,args=(f"doing research about {text}",))
        t2 = threading.Thread(target=search,args=(text,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        time.sleep(0.5)
        gui.press("enter")
    elif "search in google" in text:
        text = text.replace("search in google","")
        t1 = threading.Thread(target=speak,args=(f"performing research about {text} in google search engine",))
        t2 = threading.Thread(target=search_google,args=(text,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    elif "play" in text or "stop" in text or "pause" in text:
        play()
    else:
        perform_browser_action(text)
        perform_media_action(text)
        perform_scroll_action(text)
        
   except Exception as e:
       print("error : " + e)
       