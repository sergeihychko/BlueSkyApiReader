import requests
from io import BytesIO
from PIL import ImageTk, Image

class WebImage:
    def __init__(self, url):
        u = requests.get(url)
        self.image = ImageTk.PhotoImage(Image.open(BytesIO(u.content)))

    def get(self):
        return self.image