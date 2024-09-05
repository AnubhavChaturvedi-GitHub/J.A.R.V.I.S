import requests
from bs4 import BeautifulSoup

def get_weather_by_address(address):
    # Use Google to find the weather for the address
    search_url = f"https://www.google.com/search?q=weather+{address.replace(' ', '+')}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(search_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Scrape the relevant weather data
        location = soup.find("div", attrs={"id": "wob_loc"}).text
        time = soup.find("div", attrs={"id": "wob_dts"}).text
        weather = soup.find("span", attrs={"id": "wob_dc"}).text
        temp = soup.find("span", attrs={"id": "wob_tm"}).text
        
        weather_report = (f"Weather: {weather}\n"
                          f"Temperature: {temp}°C")
        
        return weather_report
    else:
        return "Error retrieving weather data."

