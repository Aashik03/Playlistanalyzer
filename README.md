
# 🎧 Spotify Playlist Analyzer

A sleek, Python-powered web app that connects to the Spotify API to **search tracks, explore playlists, and analyze audio features** like danceability, energy, tempo, and more. Built with Flask, it demonstrates how Python can play nice with modern APIs and frontend interactivity.

---

## 🚀 Features

- 🎵 **Search Tracks** by name and get artist info + Spotify preview link  
- 📂 **Search Playlists** with any keyword  
- 📊 **Analyze Tracks** for audio features like:
  - Danceability
  - Energy
  - Tempo
  - Acousticness
  - Valence (mood)
- 👤 OAuth2 **Login with Spotify**
- 💻 Interactive **frontend using HTML + JavaScript**
- 💬 Error handling & default values for clean UX

---

## 🔧 Tech Stack

- **Python (Flask)** – server-side logic & API handling  
- **Spotify Web API** – track & playlist data  
- **HTML/CSS/JS** – frontend UI  
- **Dotenv** – secure env variable management  
- **Requests** – HTTP requests to Spotify API

---

## 🧠 Skills Demonstrated

- API authentication using **OAuth2**
- RESTful API consumption with **`requests`**
- JSON parsing and data manipulation
- Flask **routing, sessions**, and dynamic response
- Frontend-backend interaction
- Error handling + fallback logic
- Clear project structure and clean code

---

## 🚦 Getting Started

1. Clone the repo
2. Add your `.env` file with these variables:
   ```env
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_secret
   SPOTIFY_REDIRECT_URI=http://localhost:3000/callback
   FLASK_SECRET_KEY=anything_secret
   ```
3. Run the Flask app:
   ```bash
   python app.py
   ```

4. Visit `http://localhost:3000` in your browser and jam out.

---

## 🤔 Why This Project?

This was built to showcase real-world Python skills beyond basic scripts—**OAuth integration, working with live data, designing APIs, and building interactive apps**. It’s not just a script, it’s a real app.

---


## 💬 Future Enhancements

- Playlist mood graph using Chart.js
- Save history of searches
- UI polish with Tailwind or Bootstrap
- Deploy to Render/Netlify

---


![Screenshot 2025-05-09 095834](https://github.com/user-attachments/assets/c87edcbc-9e0d-43b8-a63a-e7d4804d3668)
