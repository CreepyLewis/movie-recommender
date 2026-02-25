import streamlit as st
import requests

# =========================
# CONFIG
# =========================
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
LOGO_BASE = "https://image.tmdb.org/t/p/w200"

st.set_page_config(page_title="Creepy Movie Recommendation", layout="wide")

# =========================
# NETFLIX DARK UI + HOVER
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #0e0e0e;
    color: white;
}

h1,h2,h3,h4,h5 {
    color: white;
}

.movie-card {
    position: relative;
    cursor: pointer;
}

.movie-card img {
    width: 100%;
    border-radius: 10px;
    transition: transform 0.3s ease;
}

.movie-card:hover img {
    transform: scale(1.08);
}

.overlay {
    position: absolute;
    bottom: 0;
    width: 100%;
    padding: 12px;
    background: linear-gradient(to top, rgba(0,0,0,0.9), transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
    border-radius: 10px;
}

.movie-card:hover .overlay {
    opacity: 1;
}

.overlay h4 {
    margin: 0;
    font-size: 14px;
}

.overlay p {
    margin: 0;
    font-size: 12px;
    color: #ccc;
}

.play-icon {
    position: absolute;
    top: 40%;
    left: 45%;
    font-size: 40px;
    color: white;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.movie-card:hover .play-icon {
    opacity: 1;
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 Creepy Movie Recommendation")

# =========================
# QUERY PARAMS (SAME TAB NAVIGATION)
# =========================
query_params = st.query_params
if "movie_id" in query_params:
    try:
        st.session_state.selected_id = int(query_params["movie_id"][0])
    except:
        pass

# =========================
# API FUNCTIONS (SAFE)
# =========================
def safe_get(url, params):
    try:
        res = requests.get(url, params=params)
        data = res.json()
        return data
    except:
        return {}

def get_movies(endpoint):
    data = safe_get(f"{BASE_URL}{endpoint}", {"api_key": TMDB_API_KEY})
    return data.get("results", [])

def search_movies(query):
    data = safe_get(f"{BASE_URL}/search/movie",
                    {"api_key": TMDB_API_KEY, "query": query})
    return data.get("results", [])

def get_movie_details(movie_id):
    return safe_get(f"{BASE_URL}/movie/{movie_id}",
                    {"api_key": TMDB_API_KEY})

def get_trailer(movie_id):
    data = safe_get(f"{BASE_URL}/movie/{movie_id}/videos",
                    {"api_key": TMDB_API_KEY})
    for vid in data.get("results", []):
        if vid.get("type") == "Trailer" and vid.get("site") == "YouTube":
            return f"https://www.youtube.com/embed/{vid['key']}"
    return None

def get_actors(movie_id):
    data = safe_get(f"{BASE_URL}/movie/{movie_id}/credits",
                    {"api_key": TMDB_API_KEY})
    return data.get("cast", [])[:6]

def get_watch_providers(movie_id):
    data = safe_get(f"{BASE_URL}/movie/{movie_id}/watch/providers",
                    {"api_key": TMDB_API_KEY})
    return data.get("results", {}).get("KE", {})

# =========================
# DISPLAY MOVIE ROW
# =========================
def display_row(title, endpoint):
    st.subheader(title)
    movies = get_movies(endpoint)

    if not movies:
        return

    cols = st.columns(6)

    for i, movie in enumerate(movies[:18]):
        poster = movie.get("poster_path")
        if not poster:
            continue

        title_text = movie.get("title", "Unknown")
        rating = movie.get("vote_average", "N/A")
        year = movie.get("release_date", "")[:4]

        with cols[i % 6]:
            st.markdown(f"""
            <div class="movie-card"
                 onclick="window.location.href='?movie_id={movie['id']}';">
                <img src="{IMAGE_BASE + poster}">
                <div class="play-icon">▶</div>
                <div class="overlay">
                    <h4>{title_text}</h4>
                    <p>⭐ {rating} | {year}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

# =========================
# SEARCH BAR
# =========================
search_query = st.text_input("🔍 Search for a movie")

if search_query:
    movies = search_movies(search_query)
    if movies:
        display_row("Search Results", f"/search/movie?query={search_query}")
    else:
        st.warning("No movies found.")
else:
    display_row("🔥 Popular", "/movie/popular")
    display_row("💥 Action", "/discover/movie?with_genres=28")
    display_row("😂 Comedy", "/discover/movie?with_genres=35")
    display_row("👻 Horror", "/discover/movie?with_genres=27")
    display_row("❤️ Romance", "/discover/movie?with_genres=10749")

# =========================
# MOVIE DETAILS PAGE
# =========================
if "selected_id" in st.session_state:

    movie_id = st.session_state.selected_id
    movie = get_movie_details(movie_id)

    if movie:
        st.divider()

        col1, col2 = st.columns([1,2])

        with col1:
            if movie.get("poster_path"):
                st.image(IMAGE_BASE + movie["poster_path"])

        with col2:
            st.subheader(movie.get("title", "Unknown"))
            st.write(f"⭐ Rating: {movie.get('vote_average','N/A')}")
            st.write(f"📅 Release: {movie.get('release_date','N/A')}")
            st.write(movie.get("overview","No description available."))

        # Trailer
        trailer = get_trailer(movie_id)
        if trailer:
            st.markdown("### ▶ Trailer")
            st.markdown(
                f'<iframe width="100%" height="400" src="{trailer}" frameborder="0" allowfullscreen></iframe>',
                unsafe_allow_html=True
            )

        # Actors
        cast = get_actors(movie_id)
        if cast:
            st.markdown("### 🎭 Top Cast")
            cols = st.columns(len(cast))
            for i, actor in enumerate(cast):
                with cols[i]:
                    if actor.get("profile_path"):
                        st.image(IMAGE_BASE + actor["profile_path"])
                    st.caption(actor.get("name",""))

        # Watch Providers
        providers = get_watch_providers(movie_id)
        if providers:
            st.markdown("### 📺 Available in Kenya")

            for section in ["flatrate","rent","buy"]:
                if section in providers:
                    cols = st.columns(len(providers[section]))
                    for i, p in enumerate(providers[section]):
                        with cols[i]:
                            if p.get("logo_path"):
                                st.image(LOGO_BASE + p["logo_path"])
                            if providers.get("link"):
                                st.markdown(
                                    f"[Watch Now]({providers['link']})"
                                )
        else:
            st.warning("Not available in Kenya.")
