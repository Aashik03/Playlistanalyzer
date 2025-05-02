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

if __name__ == '__main__':
    app.run(debug=True, port=3000)
