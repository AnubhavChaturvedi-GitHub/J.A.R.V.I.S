import pyautogui

def scroll_up():
    # Scroll up by pressing the Up arrow key five times
    pyautogui.press('up', presses=5)

def scroll_down():
    # Scroll down by pressing the Down arrow key five times
    pyautogui.press('down', presses=5)

def scroll_to_top():
    # Scroll to the top of the page
    pyautogui.hotkey('home')

def scroll_to_bottom():
    # Scroll to the bottom of the page
    pyautogui.hotkey('end')

def perform_scroll_action(text):
    if "scroll up" in text or "upar scroll karo" in text:
        scroll_up()
    elif "scroll down" in text or "neeche scroll karo" in text:
        scroll_down()
    elif "scroll to top" in text or "shuruat par jao" in text:
        scroll_to_top()
    elif "scroll to bottom" in text or "ant par jao" in text:
        scroll_to_bottom()
    else:
        pass

