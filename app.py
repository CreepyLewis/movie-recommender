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

def get_recommendations(movie_id, limit=12):
    """Get recommended movies for a given movie_id."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={TMDB_API_KEY}"
    response = requests.get(url).json()
    recs = response.get("results", [])
    recommendations = []
    for r in recs[:limit]:
        recommendations.append({
            "title": r["title"],
            "poster": TMDB_IMAGE_BASE + r["poster_path"] if r.get("poster_path") else None
        })
    return recommendations

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")
st.markdown("<h1 style='text-align: center;'>🎬 Movie Recommender (Netflix Style)</h1>", unsafe_allow_html=True)

# Search input
movie_name = st.text_input("Search for a movie:")

if movie_name:
    movie = search_movie(movie_name)
    
    if movie:
        movie_id = movie["id"]
        poster_url = TMDB_IMAGE_BASE + movie["poster_path"] if movie.get("poster_path") else None

        # Main movie display
        st.markdown(f"### 🎥 {movie['title']}", unsafe_allow_html=True)
        if poster_url:
            st.image(poster_url, width=300)
        else:
            st.write("Poster not available")

        # Recommendations
        recs = get_recommendations(movie_id, limit=12)
        if recs:
            st.markdown("### You might also like:")
            
            # Scrollable horizontal layout
            scroll_container = st.container()
            scroll_html = "<div style='display:flex; overflow-x:auto;'>"
            for rec in recs:
                poster_html = f"""
                <div style='margin-right:10px; text-align:center; flex:0 0 auto;'>
                    <img src='{rec['poster']}' width='150'><br>
                    <span style='font-size:14px;'>{rec['title']}</span>
                </div>
                """ if rec['poster'] else f"<div style='margin-right:10px;'>{rec['title']}</div>"
                scroll_html += poster_html
            scroll_html += "</div>"
            scroll_container.markdown(scroll_html, unsafe_allow_html=True)
        else:
            st.write("No recommendations found.")
    else:
        st.write("Movie not found. Please check the spelling.")
