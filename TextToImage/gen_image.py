import requests
from PIL import Image
from io import BytesIO

def generate_image(text):
    url = 'https://api.airforce/v1/imagine2'
    params = {'prompt': text}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        image.save('generated_image.png')
        image.show()
        print('Image saved as generated_image.png')
    else:
        print(f'Failed to retrieve image. Status code: {response.status_code}')
