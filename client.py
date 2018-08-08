import os
import requests
from threading import Timer
from simplecrypt import encrypt, decrypt
import random

url = 'http://192.168.1.106:5001/upload'
post_fields = {'image': '@./static/trump-test.jpg', 'token': 'RDRDRD'}

def send_image():
	# open picture
	file = open('static/trump-test.jpg', 'rb')
	# encrypt picture
	filename = ("%020x" % random.randrange(16**30))[:16]
	encrypt_image("kkk", filename, file.read())
	# open encrypted picture
	file = open(filename, 'rb')
	image = {'image': file}
	# send to server
	r = requests.post(url, files=image, data=post_fields)
	print(r.text)
	os.remove(filename)
	t = Timer(7.0, send_image)
	t.start()

def encrypt_image(key, filename, data):
	with open(filename, 'wb') as output:
		cipher = encrypt(key, data)
		output.write(cipher)


send_image()
#encrypt_image("kkk", "output", file.read())



#request = Request(url, urlencode(post_fields).encode())

#json = urlopen(request).read().decode()
#print(json)


