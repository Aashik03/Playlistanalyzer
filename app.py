from flask import Flask, redirect, request,jsonify, session,render_template	
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
    access_token= session.get("access_token")
    if not access_token:
        return redirect("/")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    data = response.json()

    return jsonify(data)

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
        "limit": 5  # Get multiple songs, not just one
    }

    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
    data = response.json()

    try:
        tracks = data["tracks"]["items"]
        results = []
        for track in tracks:
            results.append({
                "song": track["name"],
                "artist": track["artists"][0]["name"],
                "preview_url": track["preview_url"],
                "spotify_url": track["external_urls"]["spotify"]
            })
        return jsonify({"results": results})  # <==== VERY IMPORTANT
    except (KeyError, IndexError):
        return jsonify({"results": []})  # <=== still return an empty list if error

    
if __name__ == '__main__':
    app.run(port=3000)
