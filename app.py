import streamlit as st
import requests

# ===================================
# CONFIG
# ===================================
st.set_page_config(layout="wide")

try:
    TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
except:
    st.error("TMDB API key missing. Add it in Streamlit Secrets.")
    st.stop()

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_URL = "https://image.tmdb.org/t/p/w500"

# ===================================
# DARK NETFLIX STYLE
# ===================================
st.markdown("""
<style>
.stApp {
    background-color: #0f0f0f;
    color: white;
}
div[data-testid="stImage"] img {
    border-radius: 12px;
    transition: 0.3s;
}
div[data-testid="stImage"] img:hover {
    transform: scale(1.07);
}
button[kind="primary"] {
    background-color: red !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ===================================
# SESSION STATE
# ===================================
if "favorites" not in st.session_state:
    st.session_state.favorites = []

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

# ===================================
# TMDB FUNCTIONS
# ===================================
def search_movies(query):
    url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "include_adult": False
    }

    r = requests.get(url, params=params)

    if r.status_code != 200:
        st.error(f"API Error: {r.json().get('status_message')}")
        return []

    return r.json().get("results", [])

def get_trailer(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/videos"
    params = {"api_key": TMDB_API_KEY}
    r = requests.get(url, params=params)

    if r.status_code != 200:
        return None

    videos = r.json().get("results", [])
    for v in videos:
        if v["type"] == "Trailer" and v["site"] == "YouTube":
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None

def get_genre_movies(genre_id):
    url = f"{BASE_URL}/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "with_genres": genre_id,
        "sort_by": "popularity.desc"
    }

    r = requests.get(url, params=params)

    if r.status_code != 200:
        return []

    return r.json().get("results", [])

# ===================================
# HEADER
# ===================================
st.title("🎬 Creepy-Movie Recommendation 😈")

# ===================================
# SEARCH
# ===================================
st.subheader("🔍 Search Movies")

query = st.text_input("Start typing a movie name...")

if query:
    results = search_movies(query)

    if results:
        cols = st.columns(6)
        for i, movie in enumerate(results[:12]):
            with cols[i % 6]:
                if movie.get("poster_path"):
                    st.image(IMAGE_URL + movie["poster_path"])
                st.caption(f"⭐ {movie.get('vote_average')} | {movie.get('release_date','')[:4]}")
                if st.button(f"View {movie['id']}"):
                    st.session_state.selected_movie = movie
                    st.rerun()
    else:
        st.warning("No movies found.")

# ===================================
# MOVIE DETAILS
# ===================================
if st.session_state.selected_movie:
    movie = st.session_state.selected_movie
    st.markdown("---")
    st.header(movie["title"])

    col1, col2 = st.columns([1, 2])

    with col1:
        if movie.get("poster_path"):
            st.image(IMAGE_URL + movie["poster_path"])

    with col2:
        st.write(movie.get("overview", "No overview available."))
        st.write("⭐ Rating:", movie.get("vote_average"))
        st.write("📅 Release:", movie.get("release_date"))

        if st.button("❤️ Add to Favorites"):
            if movie not in st.session_state.favorites:
                st.session_state.favorites.append(movie)
                st.success("Added to favorites!")

        trailer_url = get_trailer(movie["id"])
        if trailer_url:
            st.link_button("🎥 Watch Trailer", trailer_url)

        if st.button("Close"):
            st.session_state.selected_movie = None
            st.rerun()

# ===================================
# FAVORITES
# ===================================
st.markdown("---")
st.subheader("❤️ Your Favorites")

if st.session_state.favorites:
    cols = st.columns(6)
    for i, movie in enumerate(st.session_state.favorites):
        with cols[i % 6]:
            if movie.get("poster_path"):
                st.image(IMAGE_URL + movie["poster_path"])
else:
    st.write("No favorites yet.")

# ===================================
# GENRE ROWS
# ===================================
st.markdown("---")
st.subheader("🔥 Popular Action")

action_movies = get_genre_movies(28)

cols = st.columns(6)
for i, movie in enumerate(action_movies[:12]):
    with cols[i % 6]:
        if movie.get("poster_path"):
            st.image(IMAGE_URL + movie["poster_path"])
