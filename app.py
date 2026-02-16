import streamlit as st
import requests
import difflib

# -----------------------------
# TMDB API config
# -----------------------------
TMDB_API_KEY = "YOUR_TMDB_API_KEY"  # Replace with your TMDB API key
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w300"
TMDB_IMAGE_ICON = "https://image.tmdb.org/t/p/w200"

# -----------------------------
# Helper Functions
# -----------------------------
def fetch_movies_by_genre(genre_id, page=1):
    """Fetch popular movies in a genre (paginated for infinite scroll)"""
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&sort_by=popularity.desc&page={page}"
    data = requests.get(url).json().get("results", [])
    movies = []
    for m in data:
        movies.append({
            "title": m["title"],
            "poster": TMDB_IMAGE_ICON + m["poster_path"] if m.get("poster_path") else None,
            "id": m["id"],
            "rating": m.get("vote_average"),
            "year": m.get("release_date", "")[:4]
        })
    return movies

def search_movie_suggestions(query, limit=10):
    """Return movie suggestions as user types (fuzzy)"""
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    results = requests.get(url).json().get("results", [])
    suggestions = []
    for m in results[:limit]:
        suggestions.append({
            "title": m["title"],
            "id": m["id"],
            "poster": TMDB_IMAGE_ICON + m["poster_path"] if m.get("poster_path") else None
        })
    return suggestions

def get_movie_details(movie_id):
    """Get detailed info with trailer"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=videos,recommendations"
    data = requests.get(url).json()
    
    # Trailer URL
    trailer_url = None
    for v in data.get("videos", {}).get("results", []):
        if v["type"] == "Trailer" and v["site"] == "YouTube":
            trailer_url = f"https://www.youtube.com/watch?v={v['key']}"
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
        "year": data.get("release_date", "")[:4],
        "trailer": trailer_url,
        "recommendations": recs
    }

# -----------------------------
# TMDB Genres (popular)
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
# Streamlit Setup
# -----------------------------
st.set_page_config(page_title="🎬 Creepy-Movie Recommendation", layout="wide")
st.markdown(
    """
    <style>
    /* Dark Netflix-like background */
    .reportview-container, .main {
        background-color: #141414;
        color: white;
    }
    /* Scrollable horizontal row */
    .scroll-row {
        display:flex;
        overflow-x:auto;
        padding:10px 0;
    }
    /* Poster hover effect */
    .poster-container {
        position: relative;
        margin-right: 10px;
        flex:0 0 auto;
    }
    .poster-container img {
        border-radius: 5px;
        transition: transform 0.3s;
    }
    .poster-container img:hover {
        transform: scale(1.1);
    }
    .poster-info {
        position:absolute;
        bottom:0;
        left:0;
        width:100%;
        background: rgba(0,0,0,0.7);
        color:white;
        text-align:center;
        font-size:12px;
        padding:3px;
        opacity:0;
        transition: opacity 0.3s;
        border-radius: 0 0 5px 5px;
    }
    .poster-container:hover .poster-info {
        opacity:1;
    }
    a {color:white; text-decoration:none;}
    </style>
    """, unsafe_allow_html=True
)

st.markdown("<h1 style='text-align:center;'>🎬 Creepy-Movie Recommendation</h1>", unsafe_allow_html=True)

# -----------------------------
# Search Box with Suggestions
# -----------------------------
search_query = st.text_input("Search for a movie:")

selected_movie = None
if search_query:
    suggestions = search_movie_suggestions(search_query)
    if suggestions:
        cols = st.columns(min(len(suggestions), 5))
        for i, movie in enumerate(suggestions[:5]):
            with cols[i]:
                if movie["poster"]:
                    st.image(movie["poster"], width=120)
                if st.button(movie["title"], key=movie["id"]):
                    selected_movie = get_movie_details(movie["id"])
    else:
        st.write("No suggestions found.")

# -----------------------------
# Display Selected Movie Details
# -----------------------------
if selected_movie:
    st.markdown(f"## 🎥 {selected_movie['title']} ({selected_movie['year']})")
    if selected_movie['poster']:
        st.image(selected_movie['poster'], width=300)
    st.markdown(f"**Rating:** {selected_movie['rating']} / 10")
    st.markdown(f"**Overview:** {selected_movie['overview']}")
    if selected_movie['trailer']:
        if st.button("Watch Trailer"):
            st.video(selected_movie['trailer'])
    # Recommendations
    if selected_movie['recommendations']:
        st.markdown("### You might also like:")
        scroll_html = "<div class='scroll-row'>"
        for rec in selected_movie['recommendations']:
            poster_html = f"""
            <div class='poster-container'>
                <a href='?movie_id={rec['id']}'>
                    <img src='{rec['poster']}' width='150'>
                    <div class='poster-info'>{rec['title']}</div>
                </a>
            </div>
            """
            scroll_html += poster_html
        scroll_html += "</div>"
        st.markdown(scroll_html, unsafe_allow_html=True)

# -----------------------------
# Netflix-style Genre Rows
# -----------------------------
st.write("---")
st.markdown("<h2>Browse by Genre</h2>", unsafe_allow_html=True)

for genre_name, genre_id in GENRES.items():
    st.markdown(f"### {genre_name}")
    page = 1
    movies_in_genre = fetch_movies_by_genre(genre_id, page=page)
    if movies_in_genre:
        scroll_html = "<div class='scroll-row'>"
        for m in movies_in_genre:
            poster_html = f"""
            <div class='poster-container'>
                <a href='?movie_id={m['id']}'>
                    <img src='{m['poster']}' width='150'>
                    <div class='poster-info'>{m['title']} ({m['year']}) | ⭐{m['rating']}</div>
                </a>
            </div>
            """
            scroll_html += poster_html
        scroll_html += "</div>"
        st.markdown(scroll_html, unsafe_allow_html=True)
