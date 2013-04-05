import requests

post_url = 'http://localhost:5000/api/v1/new'
data = {
    'text': 'Hello World!',
    'unlisted': True
}

r = requests.post(post_url, data=data)
