import streamlit as st
import requests

# ===============================
# CONFIG
# ===============================
TMDB_API_KEY = "YOUR_TMDB_API_KEY"
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_URL = "https://image.tmdb.org/t/p/w500"
ICON_URL = "https://image.tmdb.org/t/p/w200"

st.set_page_config(layout="wide")

# ===============================
# DARK NETFLIX STYLE
# ===============================
st.markdown("""
<style>
body {
    background-color: #0f0f0f;
    color: white;
}
.stApp {
    background-color: #0f0f0f;
}
.poster:hover {
    transform: scale(1.05);
    transition: 0.3s;
}
button {
    background-color: red !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# SESSION STATE
# ===============================
if "user" not in st.session_state:
    st.session_state.user = None

if "favorites" not in st.session_state:
    st.session_state.favorites = []

# ===============================
# LOGIN SYSTEM
# ===============================
def login():
    st.title("🔐 Login to Creepy-Movie")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username and password:
            st.session_state.user = username
            st.success("Logged in successfully!")
            st.rerun()

if not st.session_state.user:
    login()
    st.stop()

# ===============================
# HEADER
# ===============================
st.title("🎬 Creepy-Movie Recommendation 😈")

if st.button("Logout"):
    st.session_state.user = None
    st.rerun()

# ===============================
# TMDB FUNCTIONS
# ===============================
def search_movies(query):
    url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query
    }
    r = requests.get(url, params=params)
    if r.status_code != 200:
        st.error("API Error. Check your API Key.")
        return []
    return r.json().get("results", [])

def get_trailer(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/videos"
    params = {"api_key": TMDB_API_KEY}
    r = requests.get(url, params=params)
    data = r.json().get("results", [])
    for vid in data:
        if vid["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={vid['key']}"
    return None

def get_genre_movies(genre_id, page=1):
    url = f"{BASE_URL}/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "with_genres": genre_id,
        "page": page
    }
    r = requests.get(url, params=params)
    return r.json().get("results", [])

# ===============================
# SEARCH BAR
# ===============================
query = st.text_input("Search for a movie")

if query:
    results = search_movies(query)

    if results:
        st.subheader("Search Results")

        cols = st.columns(5)

        for i, movie in enumerate(results[:10]):
            with cols[i % 5]:
                if movie.get("poster_path"):
                    poster_url = IMAGE_URL + movie["poster_path"]
                    st.image(poster_url)

                st.caption(f"⭐ {movie.get('vote_average')} | {movie.get('release_date','')[:4]}")

                if st.button(f"Details {movie['id']}"):
                    st.session_state.selected = movie

    else:
        st.warning("No suggestions found.")

# ===============================
# MOVIE DETAILS
# ===============================
if "selected" in st.session_state:
    movie = st.session_state.selected

    st.markdown("---")
    st.header(movie["title"])

    col1, col2 = st.columns([1,2])

    with col1:
        if movie.get("poster_path"):
            st.image(IMAGE_URL + movie["poster_path"])

    with col2:
        st.write(movie.get("overview"))
        st.write("⭐ Rating:", movie.get("vote_average"))

        if st.button("Add to Favorites"):
            st.session_state.favorites.append(movie)
            st.success("Added to Favorites!")

        trailer = get_trailer(movie["id"])
        if trailer:
            st.link_button("🎥 Watch Trailer", trailer)

# ===============================
# FAVORITES
# ===============================
st.markdown("---")
st.subheader("❤️ Your Favorites")

if st.session_state.favorites:
    cols = st.columns(5)
    for i, movie in enumerate(st.session_state.favorites):
        with cols[i % 5]:
            if movie.get("poster_path"):
                st.image(IMAGE_URL + movie["poster_path"])
else:
    st.write("No favorites yet.")

# ===============================
# GENRE SECTIONS
# ===============================
st.markdown("---")
st.subheader("🔥 Popular Action Movies")

action_movies = get_genre_movies(28)

cols = st.columns(6)
for i, movie in enumerate(action_movies[:12]):
    with cols[i % 6]:
        if movie.get("poster_path"):
            st.image(IMAGE_URL + movie["poster_path"])
