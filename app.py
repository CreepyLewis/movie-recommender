import streamlit as st
import requests
import random

st.set_page_config(page_title="Creepy Movie Recommender", layout="wide")

# -----------------------------
# CONFIG
# -----------------------------
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
.movie-card img {
    border-radius: 12px;
    transition: transform 0.3s;
}
.movie-card img:hover {
    transform: scale(1.08);
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 Creepy Movie Recommender")

# -----------------------------
# API FUNCTIONS
# -----------------------------
def search_movies(query, page=1):
    url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": API_KEY,
        "query": query,
        "page": page
    }
    response = requests.get(url, params=params).json()
    return response

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

# -----------------------------
# AUTOCOMPLETE SEARCH
# -----------------------------
query = st.text_input("Search movie...")

if query:
    data = search_movies(query)
    results = data.get("results", [])

    if results:
        st.subheader("Search Results")

        cols = st.columns(5)
        for i, movie in enumerate(results[:10]):
            with cols[i % 5]:
                if movie.get("poster_path"):
                    st.image(IMG_URL + movie["poster_path"])
                st.caption(movie["title"])
                st.write(f"⭐ {movie.get('vote_average', 'N/A')}")

                if st.button("Details", key=movie["id"]):
                    details = get_movie_details(movie["id"])
                    st.subheader(details["title"])
                    st.write(details["overview"])

                    # AI Recommendation (Similar Movies)
                    st.subheader("🤖 AI Recommendations")
                    similar = get_similar(movie["id"])
                    rec_cols = st.columns(5)
                    for j, rec in enumerate(similar[:5]):
                        with rec_cols[j % 5]:
                            if rec.get("poster_path"):
                                st.image(IMG_URL + rec["poster_path"])
                            st.caption(rec["title"])
    else:
        st.warning("No suggestions found.")

# -----------------------------
# MULTIPLE GENRE ROWS
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

# -----------------------------
# LOAD MORE (Pagination)
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = 1

st.divider()
st.subheader("🎥 Browse More")

more = search_movies("popular", st.session_state.page)
movies = more.get("results", [])

cols = st.columns(5)
for i, movie in enumerate(movies[:10]):
    with cols[i % 5]:
        if movie.get("poster_path"):
            st.image(IMG_URL + movie["poster_path"])
        st.caption(movie["title"])

if st.button("Load More"):
    st.session_state.page += 1
    st.rerun()
def get_trailer(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/videos"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params).json()

    for video in response.get("results", []):
        if video["type"] == "Trailer" and video["site"] == "YouTube":
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None
