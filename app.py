import streamlit as st
import requests

# -----------------------------
# TMDB API configuration
# -----------------------------
TMDB_API_KEY = "YOUR_TMDB_API_KEY"  # Replace with your TMDB API key
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# -----------------------------
# Helper functions
# -----------------------------
def search_movie(movie_name):
    """Search for a movie by name and return the first match."""
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
    response = requests.get(url).json()
    results = response.get("results")
    if results:
        return results[0]  # Return first search result
    return None

def get_recommendations(movie_id):
    """Get recommended movies for a given movie_id."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={TMDB_API_KEY}"
    response = requests.get(url).json()
    recs = response.get("results", [])
    recommendations = []
    for r in recs[:6]:  # limit to 6 recommendations
        recommendations.append({
            "title": r["title"],
            "poster": TMDB_IMAGE_BASE + r["poster_path"] if r.get("poster_path") else None
        })
    return recommendations

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")
st.title("🎬 Movie Recommender (TMDB)")

movie_name = st.text_input("Enter a movie name:")

if movie_name:
    movie = search_movie(movie_name)
    
    if movie:
        movie_id = movie["id"]
        poster_url = TMDB_IMAGE_BASE + movie["poster_path"] if movie.get("poster_path") else None

        st.subheader(f"🎥 {movie['title']}")
        if poster_url:
            st.image(poster_url, width=250)
        else:
            st.write("Poster not available")

        # Fetch recommendations
        recs = get_recommendations(movie_id)
        if recs:
            st.write("---")
            st.subheader("You might also like:")

            # Display in Netflix-style grid
            cols = st.columns(len(recs))
            for idx, rec in enumerate(recs):
                with cols[idx]:
                    if rec["poster"]:
                        st.image(rec["poster"], width=150)
                    st.caption(rec["title"])
        else:
            st.write("No recommendations found.")
    else:
        st.write("Movie not found. Please check the spelling.")
