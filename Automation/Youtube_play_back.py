import pyautogui

def volume_up():
    pyautogui.press('up')

def volume_down():
    pyautogui.press('down')

def seek_forward():
    pyautogui.press('right')

def seek_backward():
    pyautogui.press('left')

def seek_forward_10s():
    pyautogui.press('l')

def seek_backward_10s():
    pyautogui.press('j')

def seek_backward_frame():
    pyautogui.press(',')

def seek_forward_frame():
    pyautogui.press('.')

def seek_to_beginning():
    pyautogui.press('home')

def seek_to_end():
    pyautogui.press('end')

def seek_to_previous_chapter():
    pyautogui.hotkey('ctrl', 'left')

def seek_to_next_chapter():
    pyautogui.hotkey('ctrl', 'right')

def decrease_playback_speed():
    pyautogui.hotkey('shift', ',')

def increase_playback_speed():
    pyautogui.hotkey('shift', '.')

def move_to_next_video():
    pyautogui.hotkey('shift', 'n')

def move_to_previous_video():
    pyautogui.hotkey('shift', 'p')

def perform_media_action(text):
    if "volume up" in text or "volume badhao" in text:
        volume_up()
    elif "volume down" in text or "volume ghatao" in text:
        volume_down()
    elif "seek forward" in text or "aage badhao" in text:
        seek_forward()
    elif "seek backward" in text or "peeche karo" in text:
        seek_backward()
    elif "seek forward 10 seconds" in text or "10 second aage badhao" in text:
        seek_forward_10s()
    elif "seek backward 10 seconds" in text or "10 second peeche karo" in text:
        seek_backward_10s()
    elif "seek backward frame" in text or "frame peeche karo" in text:
        seek_backward_frame()
    elif "seek forward frame" in text or "frame aage badhao" in text:
        seek_forward_frame()
    elif "seek to beginning" in text or "shuruat par jao" in text:
        seek_to_beginning()
    elif "seek to end" in text or "ant par jao" in text:
        seek_to_end()
    elif "seek to previous chapter" in text or "previous chapter par jao" in text:
        seek_to_previous_chapter()
    elif "seek to next chapter" in text or "next chapter par jao" in text:
        seek_to_next_chapter()
    elif "decrease playback speed" in text or "speed kam karo" in text:
        decrease_playback_speed()
    elif "increase playback speed" in text or "speed badhao" in text:
        increase_playback_speed()
    elif "move to next video" in text or "next video par jao" in text:
        move_to_next_video()
    elif "move to previous video" in text or "previous video par jao" in text:
        move_to_previous_video()
    else:
        pass

