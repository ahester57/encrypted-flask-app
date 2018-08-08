import os
from flask import Flask, render_template, request
from sightengine.client import SightengineClient
from simplecrypt import encrypt, decrypt

app = Flask(__name__)

UPLOAD_FOLDER = os.path.basename('static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# You'll need to register for sightengine
client = SightengineClient('403295348', 'ZSNBkHaoswcSjrbjz7hK')
#client = SightengineClient('<id>', '<secret>')

if (__name__ == "__main__"):
	app.run(host='0.0.0.0', port=5001)

def is_it_trump(faces, prob=0.8):
	invalid = True
	reason = "Not Donald J. Trump"
	for i, face in enumerate(faces):
		if 'celebrity' in face:
			if face['celebrity'][0]['prob'] > prob and face['celebrity'][0]['name'] == "Donald J. Trump":
				reason = "Contains Donald J. Trump"
				print(reason)
				invalid = False
			if face['celebrity'][0]['prob'] > 0.90 and face['celebrity'][0]['name'] == "Vladimir Putin":
				faces.pop(i)
				return is_it_trump(faces, 0.1)
	return invalid, reason

def decrypt_image(key, filename):
	with open(filename, 'rb') as inp:
		cipher = inp.read()
		plaintext = decrypt(key, cipher)
		return plaintext

@app.route('/')
def hello_world():
	return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
	try:
		file = request.files['image']
		f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
		
		invalid = True
		reason = "Not Donald J. Trump"
		dec_f = ("%s_dec.jpg" % f)
	except:
		reason = "Missing Image"
		return render_template('index.html', invalidImage=True, reason=reason, init=True, filename="")


	try:
		if len(request.form) > 0:
			token = request.form['token']
			if token != "RDRDRD":
				reason = "Wrong Token"
				return render_template('index.html', invalidImage=True, reason=reason, init=True, filename=f)
		else:
			reason = "Missing Token"
			return render_template('index.html', invalidImage=True, reason=reason, init=True, filename=f)
	except:
		reason = "Missing Form Data"
		return render_template('index.html', invalidImage=True, reason=reason, init=True, filename=f)

	# validate image
	try:
		print(file.filename)
		dec_f = ("%s_dec.jpg" % f)

		file.save(f)
		with open(dec_f, 'wb') as dec:
			dec.write(decrypt_image("laser32097n34209f", f))


		output = client.check('nudity', 'wad', 'celebrities', 'face-attributes').set_file(dec_f)
		print(output)

		if output['status'] == "failure":
			os.remove(dec_f)
			reason = output['error']['message']
			print(reason)
			return render_template('index.html', invalidImage=invalid, reason=reason, init=True, filename=f)
		
		if len(output['faces']) < 1:
			os.remove(dec_f)
			reason = "Not Donald J. Trump"
			print(reason)
			invalid = True
			return render_template('index.html', invalidImage=invalid, reason=reason, init=True, filename=f)
			
		if output['nudity']['safe'] <= output['nudity']['partial'] and output['nudity']['safe'] <= output['nudity']['raw']:
			os.remove(dec_f)
			reason = "Contains Nudity"
			print(reason)
			invalid = True
			return render_template('index.html', invalidImage=invalid, reason=reason, init=True, filename=f)

		if output['weapon'] > 0.33 or output['alcohol'] > 0.33 or output['drugs'] > 0.33:
			os.remove(dec_f)
			reason = "Contains Weapons, Alcohol, or Drugs"
			print(reason)
			invalid = True
			return render_template('index.html', invalidImage=invalid, reason=reason, init=True, filename=f)

		# is it trump
		invalid, reason = is_it_trump(output['faces'])

		if 'faces' in output:
			if output['faces'][0]['attributes']['minor'] > 0.85:
				reason = "Contains a child"
				print(reason)
				invalid = True
	finally:
		try:
			os.remove(f)
			if invalid:
				os.remove(dec_f)
		except:
			pass

	return render_template('index.html', invalidImage=invalid, reason=reason, init=True, filename=dec_f)

