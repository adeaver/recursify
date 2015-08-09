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
        if client.is_verified():
            return render_template("verify.html", name=client.get_user_first_name())

        if "code" in request.args:
            token = client.get_access_token(request.args["code"])
            client.initialize_spotify_client(token)
            if client.is_verified():
                return render_template("verify.html", name=client.get_user_first_name())
        else:
            redirect_url = client.get_redirect_url()
            return redirect(redirect_url)

    return "Bad Request"

@app.route('/selectartist', methods=['GET'])
def select():
    if request.method == "GET":
        if "search_artist" in request.args:
            artists = client.select_artist(request.args["search_artist"])
            return render_template("select.html", artists=artists)
    return "Bad Request"

@app.route('/buildplaylist', methods=['GET'])
def build():
    if request.method == "GET":
        if "selection_uri" in request.args and "selection_name" in request.args:
            client.set_playlist_title(request.args['selection_name'])
            return render_template("build.html", artist_name=request.args["selection_name"],
            artist_uri=request.args["selection_uri"])
    return "Bad Request"

@app.route('/complete', methods=['GET'])
def complete():
    if request.method == "GET":
        if "uri" in request.args:
            artists = client.get_all_related(request.args['uri'], 3)
            new_artists = client.clean_shuffle_cut(artists, 30)
            songs = client.create_song_list(new_artists, 100)
            message = client.create_playlist(songs)
            return message
    return "Bad Request"