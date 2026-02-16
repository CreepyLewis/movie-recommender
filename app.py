import streamlit as st
import requests
import difflib

# -----------------------------
# TMDB API configuration
# -----------------------------
TMDB_API_KEY = "YOUR_TMDB_API_KEY"  # Replace with your TMDB API key
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w200"  # smaller icons for search

# -----------------------------
# Helper functions
# -----------------------------
def fetch_popular_movies(limit=500):
    """Fetch a large list of popular movies from TMDB"""
    movies = []
    for page in range(1, (limit // 20) + 2):  # TMDB returns 20 per page
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&page={page}"
        data = requests.get(url).json().get("results", [])
        for m in data:
            movies.append({
                "title": m["title"],
                "poster": TMDB_IMAGE_BASE + m["poster_path"] if m.get("poster_path") else None
            })
        if len(movies) >= limit:
            break
    return movies[:limit]

def search_movies(movie_list, query):
    """Filter movies by search query using fuzzy matching"""
    titles = [m["title"] for m in movie_list]
    closest = difflib.get_close_matches(query, titles, n=50, cutoff=0.1)
    results = [m for m in movie_list if m["title"] in closest or query.lower() in m["title"].lower()]
    return results

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="🎬 MovieBox", layout="wide")
st.markdown("<h1 style='text-align:center;'>🎬 MovieBox</h1>", unsafe_allow_html=True)

# Load popular movies (can cache to speed up)
@st.cache_data(show_spinner=True)
def load_movies():
    return fetch_popular_movies(limit=500)  # adjust number of movies

movie_list = load_movies()

# Search bar
search_query = st.text_input("Search movies...")

# Filter movies
if search_query:
    filtered_movies = search_movies(movie_list, search_query)
else:
    filtered_movies = movie_list[:50]  # show first 50 if no search

# Display movies in a grid with posters
cols_per_row = 5
for i in range(0, len(filtered_movies), cols_per_row):
    cols = st.columns(cols_per_row)
    for j, movie in enumerate(filtered_movies[i:i+cols_per_row]):
        with cols[j]:
            if movie["poster"]:
                st.image(movie["poster"], width=120)
            st.caption(movie["title"])
