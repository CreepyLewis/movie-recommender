import streamlit as st
import requests

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Creepy-Movie Recommendation", layout="wide")

API_KEY = st.secrets["TMDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"
IMG_URL = "https://image.tmdb.org/t/p/w500"

# -----------------------------
# DARK NETFLIX STYLE
# -----------------------------
st.markdown("""
<style>
body {
    background-color: #0e0e0e;
    color: white;
}
section[data-testid="stSidebar"] {
    background-color: #111111;
}
.stApp {
    background-color: #0e0e0e;
}
img {
    border-radius: 12px;
    transition: transform 0.3s ease;
}
img:hover {
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 Creepy-Movie Recommendation")

# -----------------------------
# API FUNCTIONS
# -----------------------------
def search_movies(query):
    url = f"{BASE_URL}/search/movie"
    params = {"api_key": API_KEY, "query": query}
    return requests.get(url, params=params).json()

def get_movies_by_genre(genre_id):
    url = f"{BASE_URL}/discover/movie"
    params = {
        "api_key": API_KEY,
        "with_genres": genre_id,
        "sort_by": "popularity.desc"
    }
    response = requests.get(url, params=params).json()
    return response.get("results", [])

def get_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {"api_key": API_KEY}
    return requests.get(url, params=params).json()

def get_similar(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/similar"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params).json()
    return response.get("results", [])

def get_trailer(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/videos"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params).json()

    for video in response.get("results", []):
        if video["type"] == "Trailer" and video["site"] == "YouTube":
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None

def get_watch_providers_kenya(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/watch/providers"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params).json()
    return response.get("results", {}).get("KE", {})

# -----------------------------
# SEARCH SECTION
# -----------------------------
query = st.text_input("🔍 Search for a movie")

if query:
    data = search_movies(query)
    results = data.get("results", [])

    if results:
        st.subheader("Search Results")
        cols = st.columns(5)

        for i, movie in enumerate(results[:10]):
            with cols[i % 5]:
                if movie.get("poster_path"):
                    if st.button(" ", key=f"poster_{movie['id']}"):
                        st.session_state.selected_movie = movie["id"]

                    st.image(IMG_URL + movie["poster_path"])

                st.caption(movie["title"])
    else:
        st.warning("No suggestions found.")

# -----------------------------
# MOVIE DETAILS SECTION
# -----------------------------
if "selected_movie" in st.session_state:

    movie_id = st.session_state.selected_movie
    details = get_movie_details(movie_id)
    trailer_url = get_trailer(movie_id)
    providers = get_watch_providers_kenya(movie_id)

    st.divider()
    st.subheader(details["title"])

    col1, col2 = st.columns([1, 2])

    with col1:
        if details.get("poster_path"):
            st.image(IMG_URL + details["poster_path"])

    with col2:
        st.write(f"⭐ Rating: {details.get('vote_average', 'N/A')}")
        st.write(f"📅 Release Date: {details.get('release_date', 'N/A')}")
        st.write(details.get("overview", "No description available."))

        if trailer_url:
            st.video(trailer_url)
        else:
            st.warning("Trailer not available.")

    # -----------------------------
    # WATCH PROVIDERS SECTION
    # -----------------------------
    st.subheader("📺 Where to Watch in Kenya")

    if providers:
        if "flatrate" in providers:
            st.write("Subscription:")
            for p in providers["flatrate"]:
                st.write("•", p["provider_name"])

        if "rent" in providers:
            st.write("Rent:")
            for p in providers["rent"]:
                st.write("•", p["provider_name"])

        if "buy" in providers:
            st.write("Buy:")
            for p in providers["buy"]:
                st.write("•", p["provider_name"])
    else:
        st.warning("Not available in Kenya.")

    # -----------------------------
    # SIMILAR MOVIES
    # -----------------------------
    st.subheader("🤖 Similar Movies")
    similar = get_similar(movie_id)

    sim_cols = st.columns(5)
    for j, rec in enumerate(similar[:5]):
        with sim_cols[j % 5]:
            if rec.get("poster_path"):
                st.image(IMG_URL + rec["poster_path"])
            st.caption(rec["title"])

# -----------------------------
# GENRE ROWS (NETFLIX STYLE)
# -----------------------------
st.divider()

st.subheader("🔥 Popular Action")
action_movies = get_movies_by_genre(28)
cols = st.columns(6)
for i, movie in enumerate(action_movies[:6]):
    with cols[i]:
        if movie.get("poster_path"):
            st.image(IMG_URL + movie["poster_path"])
        st.caption(movie["title"])

st.subheader("😂 Comedy")
comedy_movies = get_movies_by_genre(35)
cols = st.columns(6)
for i, movie in enumerate(comedy_movies[:6]):
    with cols[i]:
        if movie.get("poster_path"):
            st.image(IMG_URL + movie["poster_path"])
        st.caption(movie["title"])

st.subheader("😱 Horror")
horror_movies = get_movies_by_genre(27)
cols = st.columns(6)
for i, movie in enumerate(horror_movies[:6]):
    with cols[i]:
        if movie.get("poster_path"):
            st.image(IMG_URL + movie["poster_path"])
        st.caption(movie["title"])
