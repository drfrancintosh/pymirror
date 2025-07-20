import requests

API_KEY = "AIzaSyACJptoiAZnga_eClrfFfQ6MTVvTjr1RNs"
center = "37.4971,-77.7305"
zoom = 13
size = "800x600"

url = f"https://maps.googleapis.com/maps/api/staticmap?center={center}&zoom={zoom}&size={size}&maptype=roadmap&key={API_KEY}"
img = requests.get(url)

with open("google_map.png", "wb") as f:
    f.write(img.content)
