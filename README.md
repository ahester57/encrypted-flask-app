To run web app:

	$ pip3 install flask sightengine simple-crypt
    $ export FLASK_APP=server.py
	$ flask run --host 0.0.0.0 --port 5001

To allow connections from other devices on you network, edit the iptables on
your host machine.

    $ sudo iptables -I INPUT -p tcp --dport 5001 -j ACCEPT

To upload a file visit host:5001/ in a web browser, or you can use curl.

    $ curl -X POST -F image=@<file_path> -F token="RDRDRD" <host>:5001/upload


	
