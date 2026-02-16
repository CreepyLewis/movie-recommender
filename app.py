import streamlit as st
import requests
import difflib

# -----------------------------
# TMDB API configuration
# -----------------------------
TMDB_API_KEY = "YOUR_TMDB_API_KEY"  # Replace with your TMDB API key
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# -----------------------------
# Helper functions
# -----------------------------
def fetch_movies_by_genre(genre_id, limit=12):
    """Fetch popular movies in a genre"""
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&sort_by=popularity.desc"
    data = requests.get(url).json().get("results", [])
    movies = []
    for m in data[:limit]:
        movies.append({
            "title": m["title"],
            "poster": TMDB_IMAGE_BASE + m["poster_path"] if m.get("poster_path") else None
        })
    return movies

def search_movie_fuzzy(movie_name):
    """Search TMDB for a movie, with fuzzy match fallback"""
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
    results = requests.get(url).json().get("results", [])
    if results:
        titles = [r["title"] for r in results]
        closest = difflib.get_close_matches(movie_name, titles, n=1)
        if closest:
            for r in results:
                if r["title"] == closest[0]:
                    return r
        return results[0]  # fallback: return first result
    return None

def get_recommendations(movie_id, limit=12):
    """Get recommended movies for a given movie_id"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={TMDB_API_KEY}"
    data = requests.get(url).json().get("results", [])
    recommendations = []
    for r in data[:limit]:
        recommendations.append({
            "title": r["title"],
            "poster": TMDB_IMAGE_BASE + r["poster_path"] if r.get("poster_path") else None
        })
    return recommendations

# -----------------------------
# TMDB Genre IDs (popular ones)
# -----------------------------
GENRES = {
    "Action": 28,
    "Adventure": 12,
    "Animation": 16,
    "Comedy": 35,
    "Crime": 80,
    "Documentary": 99,
    "Drama": 18,
    "Family": 10751,
    "Fantasy": 14,
    "History": 36,
    "Horror": 27,
    "Romance": 10749,
    "Sci-Fi": 878,
    "Thriller": 53
}

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="🎬 Netflix Style Movie Recommender", layout="wide")
st.markdown("<h1 style='text-align:center;'>🎬 Netflix-Style Movie Recommender</h1>", unsafe_allow_html=True)

# Search section
movie_name = st.text_input("Search for a movie:")

if movie_name:
    movie = search_movie_fuzzy(movie_name)
    if movie:
        movie_id = movie["id"]
        poster_url = TMDB_IMAGE_BASE + movie["poster_path"] if movie.get("poster_path") else None
        st.markdown(f"### 🎥 {movie['title']}", unsafe_allow_html=True)
        if poster_url:
            st.image(poster_url, width=300)
        else:
            st.write("Poster not available")

        # Recommendations
        recs = get_recommendations(movie_id, limit=12)
        if recs:
            st.markdown("### You might also like:")
            # Horizontal scrollable row
            scroll_html = "<div style='display:flex; overflow-x:auto;'>"
            for r in recs:
                poster_html = f"""
                <div style='margin-right:10px; text-align:center; flex:0 0 auto;'>
                    <img src='{r['poster']}' width='150'><br>
                    <span style='font-size:14px;'>{r['title']}</span>
                </div>
                """ if r['poster'] else f"<div style='margin-right:10px;'>{r['title']}</div>"
                scroll_html += poster_html
            scroll_html += "</div>"
            st.markdown(scroll_html, unsafe_allow_html=True)
        else:
            st.write("No recommendations found.")
    else:
        st.write("Movie not found. Please check the spelling.")

st.write("---")

# -----------------------------
# Genre rows (Netflix homepage style)
# -----------------------------
for genre_name, genre_id in GENRES.items():
    st.markdown(f"### {genre_name}")
    movies_in_genre = fetch_movies_by_genre(genre_id, limit=12)
    if movies_in_genre:
        scroll_html = "<div style='display:flex; overflow-x:auto;'>"
        for m in movies_in_genre:
            poster_html = f"""
            <div style='margin-right:10px; text-align:center; flex:0 0 auto;'>
                <img src='{m['poster']}' width='150'><br>
                <span style='font-size:14px;'>{m['title']}</span>
            </div>
            """ if m['poster'] else f"<div style='margin-right:10px;'>{m['title']}</div>"
            scroll_html += poster_html
        scroll_html += "</div>"
        st.markdown(scroll_html, unsafe_allow_html=True)
