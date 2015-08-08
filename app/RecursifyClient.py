import spotipy, random, time, urllib, requests, json
import spotipy.util as util

class RecursifyClient():
    def __init__(self, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI):
        self.CLIENT_ID = CLIENT_ID
        self.CLIENT_SECRET = CLIENT_SECRET
        self.REDIRECT_URI = REDIRECT_URI
        self.SP_CLIENT = None
        self.ROOT_ARTIST_URI = None
        self.PLAYLIST_TITLE = None
        self.USERNAME = None
        self.SCOPE = "playlist-modify-private user-library-read"

    def get_redirect_url(self):
        base_url = "https://accounts.spotify.com/authorize?"
        params = {"scope":self.SCOPE, "redirect_uri":self.REDIRECT_URI, "response_type":"code", "client_id":self.CLIENT_ID}
        base_url += urllib.urlencode(params)
        return base_url

    def get_access_token(self, response_code):
        token = ""
        data_headers = {"grant_type":"authorization_code", "code":response_code, "redirect_uri":self.REDIRECT_URI, "client_id":self.CLIENT_ID, "client_secret":self.CLIENT_SECRET}

        try:
            response = requests.post('https://accounts.spotify.com/api/token', data=data_headers)
            print response
            response_data = response.json()
            print response_data
            token = response_data['access_token']
        except:
            print "An error occurred attempting to get token"

        return token

    def get_user_first_name(self):
        if self.SP_CLIENT is not None:
            return self.SP_CLIENT.current_user()['display_name'].split()[0]
        print "An error occurred attempting to get user"
        return ""

    def initialize_spotify_client(self, token):
        self.SP_CLIENT = spotipy.Spotify(auth=token)

    def authorize(self, username):
        self.USERNAME = username
        token = util.prompt_for_user_token(username, self.SCOPE, self.CLIENT_ID, self.CLIENT_SECRET, self.REDIRECT_URI)
        if token:
            self.SP_CLIENT = spotipy.Spotify(auth=token)

    def is_verified(self):
        return self.SP_CLIENT is not None

    def select_artist(self, artist_name):
        if self.SP_CLIENT is not None:
            while True:
                try:
                    get_artist = self.SP_CLIENT.search(q='artist:' + artist_name, type='artist')
                except spotipy.client.SpotifyException:
                    time.sleep(.1)
                    continue
                break

            return {artist_info['name']:artist_info['uri'] for artist_info in get_artist['artists']['items']}
        else:
            print "Could not connect to Spotify Client"
            return "Error"

    def set_playlist_title(self, artist_name):
        self.PLAYLIST_TITLE = "Recursify Playlist Based on " + artist_name

    def get_all_related(self, artist_id, depth):
        if self.SP_CLIENT is not None:
            related = []
            while True:
                try:
                    related_dict = self.SP_CLIENT.artist_related_artists(artist_id)
                    related = [artist['uri'] for artist in related_dict['artists']]
                except spotipy.client.SpotifyException:
                    time.sleep(.1)
                    continue
                break

            if depth > 1:
                for index in range(len(related)):
                    related += self.get_all_related(related[index], depth-1)

            return related
        else:
            print "Could not connect to Spotify Client"
            return []

    def clean_list(self, param_list):
        param_list.sort()
        index = 0
        token = param_list[index]
        final_list = []

        while index < len(param_list)-1:
            index += 1
            if(param_list[index] != token):
                token = param_list[index]
                final_list.append(token)

        return final_list

    def clean_shuffle_cut(self, param_list, amount):
        args = self.clean_list(param_list)
        random.shuffle(args)
        if amount >= len(args):
            amount = len(args) - 1
        return args[:amount]

    def clean_tracks(self, track_data):
        tracks = []
        for track in track_data:
            uri = track['uri']
            while True:
                try:
                    if(self.SP_CLIENT.current_user_saved_tracks_contains('uri')[0] == False):
                        tracks.append(uri)
                except spotipy.client.SpotifyException:
                    time.sleep(.1)
                    continue
                break
        return tracks

    def get_artist_tracks(self, artist_id):
        tracks = []
        if self.SP_CLIENT is not None:
            while True:
                try:
                    top_tracks = self.SP_CLIENT.artist_top_tracks(artist_id)
                except spotipy.client.SpotifyException:
                    time.sleep(.1)
                    continue
                break

            tracks = [track['uri'] for track in top_tracks['tracks']]
        else:
            print "Could not connect to Spotify Client"
        
        return tracks

    def create_song_list(self, artist_list, amount):
        song_list = []

        for artist in artist_list:
            song_list += self.get_artist_tracks(artist)

        new_song_list = self.clean_shuffle_cut(song_list, amount)

        return new_song_list

    def create_playlist(self, song_list):
        if self.SP_CLIENT is not None:
            while True:
                try:
                    playlist = self.SP_CLIENT.user_playlist_create(self.USERNAME, self.PLAYLIST_TITLE, public=False)
                except spotipy.client.SpotifyException:
                    time.sleep(.1)
                    continue
                break

            playlist_uri = playlist['uri']

            while True:
                try:
                    self.SP_CLIENT.user_playlist_add_tracks(self.USERNAME, playlist_uri, song_list)
                except spotipy.client.SpotifyException:
                    time.sleep(.1)
                    continue
                break

            print "Complete! Enjoy your new playlist"

        else:
            print "Could not connect to Spotify Client"