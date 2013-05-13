import requests

post_url = 'https://paste.buttscicl.es/api/v1/new'
data = {
    'text': 'Hello World!',
    'unlisted': True
}

r = requests.post(post_url, data=data)
