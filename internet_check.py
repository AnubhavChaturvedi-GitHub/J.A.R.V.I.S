import requests # pip install requests


def is_Online(url = "https://www.google.com",timeout=5):
    try:
        response = requests.get(url,timeout=timeout)
        return response.status_code >= 200 and response.status_code<300
    except requests.ConnectionError:
        return False
    



    