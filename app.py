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
# NETFLIX DARK STYLE
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #0e0e0e;
    color: white;
}

h1,h2,h3,h4 {
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
    transform: scale(1.05);
}

.overlay {
    position: absolute;
    bottom: 0;
    width: 100%;
    padding: 10px;
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

.view-btn button {
    background-color: #e50914 !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    width: 100%;
    margin-top: 5px;
}

.back-btn button {
    background-color: #555 !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    width: 150px;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 Creepy Movie Recommendation")

# =========================
# SAFE API CALL
# =========================
def safe_get(url, params):
    try:
        res = requests.get(url, params=params)
        return res.json()
    except:
        return {}

def get_movies(endpoint):
    data = safe_get(f"{BASE_URL}{endpoint}", {"api_key": TMDB_API_KEY})
    return data.get("results", [])

def search_movies(query):
    data = safe_get(f"{BASE_URL}/search/movie", {"api_key": TMDB_API_KEY, "query": query})
    return data.get("results", [])

def get_movie(movie_id):
    return safe_get(f"{BASE_URL}/movie/{movie_id}", {"api_key": TMDB_API_KEY})

def get_trailer(movie_id):
    data = safe_get(f"{BASE_URL}/movie/{movie_id}/videos", {"api_key": TMDB_API_KEY})
    for vid in data.get("results", []):
        if vid.get("type") == "Trailer" and vid.get("site") == "YouTube":
            return f"https://www.youtube.com/embed/{vid['key']}"
    return None

def get_cast(movie_id):
    data = safe_get(f"{BASE_URL}/movie/{movie_id}/credits", {"api_key": TMDB_API_KEY})
    return data.get("cast", [])[:6]

def get_providers(movie_id):
    data = safe_get(f"{BASE_URL}/movie/{movie_id}/watch/providers", {"api_key": TMDB_API_KEY})
    return data.get("results", {}).get("KE", {})

# =========================
# MOVIE ROW DISPLAY
# =========================
def display_row(title, endpoint):
    st.subheader(title)
    movies = get_movies(endpoint)

    if not movies:
        return

    cols = st.columns(6)

    for i, movie in enumerate(movies[:12]):
        poster = movie.get("poster_path")
        if not poster:
            continue

        title_text = movie.get("title")
        rating = movie.get("vote_average")
        year = movie.get("release_date", "")[:4]

        with cols[i % 6]:

            # ENTIRE CARD CLICKABLE
            if st.button("", key=f"card_{movie['id']}"):
                st.session_state.selected_id = movie["id"]
                st.rerun()

            st.markdown(f"""
            <div class="movie-card">
                <img src="{IMAGE_BASE + poster}">
                <div class="play-icon">▶</div>
                <div class="overlay">
                    <h4>{title_text}</h4>
                    <p>⭐ {rating} | {year}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # VIEW DETAILS BUTTON
            if st.button("View Details", key=f"view_{movie['id']}"):
                st.session_state.selected_id = movie["id"]
                st.rerun()

# =========================
# SEARCH
# =========================
search = st.text_input("🔍 Search for a movie")

if search:
    results = search_movies(search)
    if results:
        display_row("Search Results", f"/search/movie?query={search}")
    else:
        st.warning("No movies found.")
else:
    display_row("🔥 Popular", "/movie/popular")
    display_row("💥 Action", "/discover/movie?with_genres=28")
    display_row("😂 Comedy", "/discover/movie?with_genres=35")
    display_row("👻 Horror", "/discover/movie?with_genres=27")
    display_row("❤️ Romance", "/discover/movie?with_genres=10749")

# =========================
# DETAILS PAGE
# =========================
if "selected_id" in st.session_state:

    movie_id = st.session_state.selected_id
    movie = get_movie(movie_id)

    if movie:
        st.divider()

        col1, col2 = st.columns([1,2])

        with col1:
            if movie.get("poster_path"):
                st.image(IMAGE_BASE + movie["poster_path"])

        with col2:
            st.subheader(movie.get("title"))
            st.write(f"⭐ Rating: {movie.get('vote_average')}")
            st.write(f"📅 Release: {movie.get('release_date')}")
            st.write(movie.get("overview"))

        trailer = get_trailer(movie_id)
        if trailer:
            st.markdown("### ▶ Trailer")
            st.markdown(
                f'<iframe width="100%" height="400" src="{trailer}" frameborder="0" allowfullscreen></iframe>',
                unsafe_allow_html=True
            )

        cast = get_cast(movie_id)
        if cast:
            st.markdown("### 🎭 Top Cast")
            cols = st.columns(len(cast))
            for i, actor in enumerate(cast):
                with cols[i]:
                    if actor.get("profile_path"):
                        st.image(IMAGE_BASE + actor["profile_path"])
                    st.caption(actor.get("name"))

        providers = get_providers(movie_id)
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
                                st.markdown(f"[Watch Now]({providers['link']})")

        # =========================
        # BACK TO HOME BUTTON
        # =========================
        if st.button("⬅ Back to Home", key="back_home"):
            del st.session_state.selected_id
            st.rerun()
