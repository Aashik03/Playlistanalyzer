from flask import Flask, redirect, request, jsonify, session, render_template
import requests, os
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_unsafe_key")

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPE = "user-read-private user-read-email"

@app.route('/')
def index():
    if "access_token" not in session:
        return login()
    return render_template("index.html")

def login():
    query = urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
    })
    return f'<a href="{AUTH_URL}?{query}">Log in with Spotify</a>'

@app.route('/callback')
def callback():
    code = request.args.get("code")

    res = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )

    token_data = res.json()
    access_token = token_data.get("access_token")
    session["access_token"] = access_token

    return f"<p>Access Token:</p><pre>{access_token}</pre>"

@app.route('/profile')
def profile():
    access_token = session.get("access_token")
    if not access_token:
        return redirect("/")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    return jsonify(response.json())

@app.route("/search")
def search():
    access_token = session.get("access_token")
    if not access_token:
        return redirect("/")

    query = request.args.get("q", "blinding lights")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "q": query,
        "type": "track",
        "limit": 5
    }
    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
    data = response.json()

    try:
        tracks = []
        for track in data["tracks"]["items"]:
            tracks.append({
                "song": track["name"],
                "artist": track["artists"][0]["name"],
                "preview_url": track["preview_url"],
                "spotify_url": track["external_urls"]["spotify"]
            })
        return jsonify(tracks)
    except (IndexError, KeyError):
        return jsonify({"error": "No track found!"})

@app.route('/search_playlist')
def search_playlist():
    try:
        access_token = session.get("access_token")
        if not access_token:
            return jsonify({"error": "Not authenticated. Please log in."}), 401

        query = request.args.get("q", "taylor swift")
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            "q": query,
            "type": "playlist",
            "limit": 5
        }

        response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
        print(f"Spotify Status Code: {response.status_code}")
        print("Raw Response Text:", response.text)

        if response.status_code != 200:
            return jsonify({"error": f"Spotify API error: {response.status_code}", "details": response.text}), 500

        try:
            data = response.json()
        except Exception as json_err:
            print("JSON Decode Error:", str(json_err))
            return jsonify({"error": "Failed to decode JSON from Spotify"}), 500

        if not data or "playlists" not in data:
            print("Unexpected data structure:", data)
            return jsonify({"error": "Unexpected Spotify response structure"}), 500

        playlists = data["playlists"].get("items", [])
        if not playlists:
            return jsonify({"error": "No playlists found!"})

        result = []
        for playlist in playlists:
            if not playlist:
                continue
            result.append({
                "name": playlist.get("name", "No Name"),
                "description": playlist.get("description", "No description"),
                "url": playlist["external_urls"]["spotify"],
                "image": playlist["images"][0]["url"] if playlist.get("images") else None
            })

        print("Final result:", result)
        return jsonify(result) 

    except Exception as e:
        print("Exception in /search_playlist:", str(e))
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/analyze_playlist')
def analyze_playlist():
   access_token=session.get('access_token')	
   playlist_id=request.args.get('playliist_id')
   if not access_token or not playlist_id:
       return {"error":"Missing access token or playlist ID"}
   
   headers={
       "Authorization":f"Bearer {access_token}"
   }

   tracks_url=f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
   response=requests.get(tracks_url,headers=headers)	
   data=response.json()
   track_ids=[
       item['track']['id']
       for item in data['items']
       if item['track'] and item['track'].get('id')
   ]
   return jsonify(track_ids)

'''@app.route('/analyze_audiio')
def analyze_audio():
    access_token=session.get('access_token')
    track_ids=request.args.get('track_id')
    if not access_token or not track_ids:
        return {"error":"Missing access token or track ID"}
    
    headers={
        "Authorization":f"Bearer {access_token}"
    }
    ids_param=",".join(track_ids[:100])
    url=f"https://api.spotify.com/v1/audio-features?ids={ids_param}"
    res=requests.get(url,headers=headers)
    features=res.json()
    return jsonify(features)'''

@app.route("/analyze_features")
def analyze_features():
    access_token = session.get("access_token")
    playlist_id = request.args.get("id")

    if not access_token or not playlist_id:
        return jsonify({"error": "Missing access token or playlist ID"})

    playlist_id = playlist_id.strip()  # Kill whitespace

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    track_res = requests.get(tracks_url, headers=headers)

    if track_res.status_code != 200:
        return jsonify({"error": f"Spotify API error: {track_res.status_code}", "details": track_res.text}), 500

    track_data = track_res.json()

    track_ids = [
        item["track"]["id"]
        for item in track_data.get("items", [])
        if item.get("track") and item["track"].get("id")
    ]

    if not track_ids:
        return jsonify({"error": "No valid tracks found in playlist"})

    ids_chunk = ",".join(track_ids[:100])
    features_url = f"https://api.spotify.com/v1/audio-features?ids={ids_chunk}"
    features_res = requests.get(features_url, headers=headers)

    if features_res.status_code != 200:
        return jsonify({"error": f"Spotify audio feature error: {features_res.status_code}", "details": features_res.text}), 500

    features_data = features_res.json().get("audio_features", [])

    def avg(key):
        values = [f[key] for f in features_data if f and f.get(key) is not None]
        return round(sum(values) / len(values), 3) if values else None

    analysis = {
        "average_danceability": avg("danceability"),
        "average_energy": avg("energy"),
        "average_valence": avg("valence"),
        "average_tempo": avg("tempo"),
        "average_acousticness": avg("acousticness"),
        "average_instrumentalness": avg("instrumentalness"),
        "total_tracks_analyzed": len(features_data),
    }

    return jsonify(analysis)

    

if __name__ == '__main__':
    app.run(debug=True, port=3000)
