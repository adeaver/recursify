from flask import render_template, request, abort, redirect, url_for
from RecursifyClient import RecursifyClient
from app import app
import os

REDIRECT_URI = "http://127.0.0.1:5000/verifydata"
CLIENT_ID = str(os.environ['RECURSIFY_CLIENT_ID'])
CLIENT_SECRET = str(os.environ['RECURSIFY_CLIENT_SECRET'])

client = RecursifyClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/verifydata', methods=['GET'])
def verify():
    if request.method == "GET":
        if "code" in request.args:
            print request.args["code"]
            token = client.get_access_token(request.args["code"])
            client.initialize_spotify_client(token)
        else:
            redirect_url = client.get_redirect_url()
            return redirect(redirect_url)

        if client.is_verified():
            return render_template("verify.html", name=client.get_user_first_name())
    return "Bad Request"

@app.route('/selectartist', methods=['GET'])
def select():
    if request.method == "GET":
        if "search_artist" in request.args:
            print client.select_artist(request.args["search_artist"])
            return "Good Request"
    return "Bad Request"