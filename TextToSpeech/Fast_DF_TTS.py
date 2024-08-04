import requests # pip install requests
from playsound import playsound # pip install playsound==1.2.2
import os
from typing import Union # pip install typing


def generate_audio(message: str,voice : str = "Matthew"):
    url: str = f"https://api.streamelements.com/kappa/v2/speech?voice={voice}&text={{{message}}}"

    headers = {'User-Agent':'Mozilla/5.0(Maciontosh;intel Mac OS X 10_15_7)AppleWebKit/537.36(KHTML,like Gecoko)Chrome/119.0.0.0 Safari/537.36'}
    
    try:
        result = requests.get(url=url, headers=headers)
        return result.content
    except:
        return None

def speak(message: str, voice: str = "Matthew", folder: str = "", extension: str = ".mp3") -> Union[None,str]:
    try:
        result_content = generate_audio(message,voice)
        file_path = os.path.join(folder,f"{voice}{extension}")
        with open(file_path,"wb") as file:
            file.write(result_content)
        playsound(file_path)
        os.remove(file_path)
        return None
    except Exception as e:
        print(e)

