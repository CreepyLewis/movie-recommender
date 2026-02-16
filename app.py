import streamlit as st
import requests
import difflib

# -----------------------------
# TMDB API configuration
# -----------------------------
TMDB_API_KEY = "YOUR_TMDB_API_KEY"  # Replace with your TMDB API key
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w300"
TMDB_IMAGE_ICON = "https://image.tmdb.org/t/p/w200"

# -----------------------------
# Helper functions
# -----------------------------
def search_movie_fuzzy(movie_name):
    """Search TMDB for a movie, with fuzzy matching fallback"""
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
    results = requests.get(url).json().get("results", [])
    if results:
        titles = [r["title"] for r in results]
        closest = difflib.get_close_matches(movie_name, titles, n=1)
        if closest:
            for r in results:
                if r["title"] == closest[0]:
                    return r
        return results[0]  # fallback: first result
    return None

def get_movie_details(movie_id):
    """Get detailed movie info: rating, overview, trailer"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=videos,recommendations"
    data = requests.get(url).json()
    
    # Trailer
    trailer_url = None
    videos = data.get("videos", {}).get("results", [])
    for v in videos:
        if v["type"] == "Trailer" and v["site"] == "YouTube":
            trailer_url = f"https://www.youtube.com/embed/{v['key']}"
            break

    # Recommendations
    recs = []
    for r in data.get("recommendations", {}).get("results", [])[:8]:
        recs.append({
            "title": r["title"],
            "poster": TMDB_IMAGE_ICON + r["poster_path"] if r.get("poster_path") else None,
            "id": r["id"]
        })
    
    return {
        "title": data.get("title"),
        "poster": TMDB_IMAGE_BASE + data["poster_path"] if data.get("poster_path") else None,
        "rating": data.get("vote_average"),
        "overview": data.get("overview"),
        "trailer": trailer_url,
        "recommendations": recs
    }

def fetch_movies_by_genre(genre_id, limit=12):
    """Fetch popular movies in a genre"""
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&sort_by=popularity.desc"
    data = requests.get(url).json().get("results", [])
    movies = []
    for m in data[:limit]:
        movies.append({
            "title": m["title"],
            "poster": TMDB_IMAGE_ICON + m["poster_path"] if m.get("poster_path") else None,
            "id": m["id"]
        })
    return movies

# -----------------------------
# TMDB Genre IDs
# -----------------------------
GENRES = {
    "Action": 28,
    "Adventure": 12,
    "Animation": 16,
    "Comedy": 35,
    "Drama": 18,
    "Fantasy": 14,
    "Horror": 27,
    "Romance": 10749,
    "Sci-Fi": 878,
    "Thriller": 53
}

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="🎬 MovieBox", layout="wide")
st.markdown("<h1 style='text-align:center;'>🎬 MovieBox - Netflix Style</h1>", unsafe_allow_html=True)

# -----------------------------
# Search Section
# -----------------------------
search_query = st.text_input("Search for a movie:")

selected_movie_details = None

if search_query:
    movie = search_movie_fuzzy(search_query)
    if movie:
        selected_movie_details = get_movie_details(movie["id"])
    else:
        st.write("Movie not found. Please check the spelling.")

# -----------------------------
# Display selected movie details
# -----------------------------
if selected_movie_details:
    st.markdown(f"## 🎥 {selected_movie_details['title']}")
    if selected_movie_details['poster']:
        st.image(selected_movie_details['poster'], width=300)
    st.markdown(f"**Rating:** {selected_movie_details['rating']} / 10")
    st.markdown(f"**Overview:** {selected_movie_details['overview']}")
    
    if selected_movie_details['trailer']:
        st.markdown("**Trailer:**")
        st.video(selected_movie_details['trailer'])
    
    # Display recommendations for selected movie
    if selected_movie_details['recommendations']:
        st.markdown("### You might also like:")
        scroll_html = "<div style='display:flex; overflow-x:auto;'>"
        for rec in selected_movie_details['recommendations']:
            poster_html = f"""
            <div style='margin-right:10px; text-align:center; flex:0 0 auto;'>
                <a href="?movie_id={rec['id']}"><img src='{rec['poster']}' width='150'></a><br>
                <span style='font-size:14px;'>{rec['title']}</span>
            </div>
            """ if rec['poster'] else f"<div style='margin-right:10px;'>{rec['title']}</div>"
            scroll_html += poster_html
        scroll_html += "</div>"
        st.markdown(scroll_html, unsafe_allow_html=True)

# -----------------------------
# Netflix-style genre rows
# -----------------------------
st.write("---")
st.markdown("## Browse by Genre")

for genre_name, genre_id in GENRES.items():
    st.markdown(f"### {genre_name}")
    movies_in_genre = fetch_movies_by_genre(genre_id, limit=12)
    if movies_in_genre:
        scroll_html = "<div style='display:flex; overflow-x:auto;'>"
        for m in movies_in_genre:
            poster_html = f"""
            <div style='margin-right:10px; text-align:center; flex:0 0 auto;'>
                <a href="?movie_id={m['id']}"><img src='{m['poster']}' width='150'></a><br>
                <span style='font-size:14px;'>{m['title']}</span>
            </div>
            """ if m['poster'] else f"<div style='margin-right:10px;'>{m['title']}</div>"
            scroll_html += poster_html
        scroll_html += "</div>"
        st.markdown(scroll_html, unsafe_allow_html=True)

# -----------------------------
# Handle URL click for recommendations (Optional)
# -----------------------------
import streamlit.components.v1 as components
params = st.experimental_get_query_params()
if "movie_id" in params:
    movie_id = int(params["movie_id"][0])
    selected_movie_details = get_movie_details(movie_id)
    st.experimental_rerun()
