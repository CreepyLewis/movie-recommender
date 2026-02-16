import streamlit as st
import requests

# =============================
# CONFIG
# =============================
TMDB_API_KEY = "YOUR_TMDB_API_KEY"
IMAGE_W300 = "https://image.tmdb.org/t/p/w300"
IMAGE_W200 = "https://image.tmdb.org/t/p/w200"

st.set_page_config(page_title="Creepy-Movie Recommendation", layout="wide")

# =============================
# DARK NETFLIX STYLE
# =============================
st.markdown("""
<style>
body {background-color: #141414; color: white;}
.stApp {background-color: #141414;}
h1, h2, h3, h4, h5, h6, p, div, span {color: white;}
.scroll-row {display:flex; overflow-x:auto; gap:15px; padding:10px 0;}
.poster {position:relative; transition: transform 0.3s;}
.poster:hover {transform: scale(1.1);}
.poster-info {
    position:absolute;
    bottom:0;
    background:rgba(0,0,0,0.8);
    width:100%;
    text-align:center;
    font-size:12px;
    padding:5px;
    opacity:0;
    transition:opacity 0.3s;
}
.poster:hover .poster-info {opacity:1;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🎬 Creepy-Movie Recommendation</h1>", unsafe_allow_html=True)

# =============================
# FUNCTIONS
# =============================

def search_movies(query):
    if not query:
        return []
    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": query}
    r = requests.get(url, params=params)
    if r.status_code != 200:
        st.error("Invalid TMDB API key or connection issue.")
        return []
    return r.json().get("results", [])

def movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": TMDB_API_KEY, "append_to_response": "videos,recommendations"}
    r = requests.get(url, params=params)
    return r.json()

def genre_movies(genre_id):
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "with_genres": genre_id,
        "sort_by": "popularity.desc"
    }
    r = requests.get(url, params=params)
    return r.json().get("results", [])

GENRES = {
    "Horror": 27,
    "Thriller": 53,
    "Sci-Fi": 878,
    "Fantasy": 14,
    "Drama": 18
}

# =============================
# SEARCH WITH LIVE SUGGESTIONS
# =============================
search = st.text_input("Search for a movie...")

selected_movie = None

if search:
    results = search_movies(search)
    if results:
        cols = st.columns(min(len(results[:6]), 6))
        for i, movie in enumerate(results[:6]):
            with cols[i]:
                poster = IMAGE_W200 + movie["poster_path"] if movie.get("poster_path") else None
                if poster:
                    st.image(poster, use_column_width=True)
                if st.button(movie["title"], key=movie["id"]):
                    selected_movie = movie_details(movie["id"])
    else:
        st.warning("No movies found. Try another title.")

# =============================
# SHOW SELECTED MOVIE
# =============================
if selected_movie:
    st.markdown("---")
    st.markdown(f"## 🎥 {selected_movie['title']} ({selected_movie.get('release_date','')[:4]})")

    col1, col2 = st.columns([1,2])

    with col1:
        if selected_movie.get("poster_path"):
            st.image(IMAGE_W300 + selected_movie["poster_path"])

    with col2:
        st.markdown(f"**⭐ Rating:** {selected_movie.get('vote_average')} / 10")
        st.markdown("**Overview:**")
        st.write(selected_movie.get("overview"))

        # Watch Trailer Button
        videos = selected_movie.get("videos", {}).get("results", [])
        trailer = None
        for v in videos:
            if v["type"] == "Trailer" and v["site"] == "YouTube":
                trailer = f"https://www.youtube.com/watch?v={v['key']}"
                break

        if trailer:
            if st.button("🎬 Watch Trailer"):
                st.video(trailer)

    # Recommendations
    recs = selected_movie.get("recommendations", {}).get("results", [])[:10]
    if recs:
        st.markdown("### 🔥 Recommended For You")
        html = "<div class='scroll-row'>"
        for r in recs:
            poster = IMAGE_W200 + r["poster_path"] if r.get("poster_path") else ""
            year = r.get("release_date","")[:4]
            rating = r.get("vote_average")
            html += f"""
            <div class='poster'>
                <img src='{poster}' width='150'>
                <div class='poster-info'>
                    ⭐ {rating} | {year}
                </div>
            </div>
            """
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

# =============================
# GENRE ROWS (NETFLIX STYLE)
# =============================
st.markdown("---")
st.markdown("## 🎭 Browse by Genre")

for name, gid in GENRES.items():
    st.markdown(f"### {name}")
    movies = genre_movies(gid)[:12]
    html = "<div class='scroll-row'>"
    for m in movies:
        poster = IMAGE_W200 + m["poster_path"] if m.get("poster_path") else ""
        year = m.get("release_date","")[:4]
        rating = m.get("vote_average")
        html += f"""
        <div class='poster'>
            <img src='{poster}' width='150'>
            <div class='poster-info'>
                ⭐ {rating} | {year}
            </div>
        </div>
        """
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
