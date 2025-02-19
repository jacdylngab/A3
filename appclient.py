import requests
import os

port = os.environ['FLASK_PORT']
if not port:
    port = 5000

r = requests.get('http://localhost:{}/'.format(port))
print(r.text)
