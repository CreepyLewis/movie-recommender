import streamlit as st
import requests

# ==================================
# CONFIG
# ==================================
st.set_page_config(page_title="Creepy - Kenya Movie Discovery", layout="wide")

API_KEY = st.secrets["TMDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
BACKDROP_BASE = "https://image.tmdb.org/t/p/w1280"
LOGO_BASE = "https://image.tmdb.org/t/p/w200"

# ==================================
# NETFLIX DARK STYLE
# ==================================
st.markdown("""
<style>
.stApp {
    background-color: #141414;
    color: white;
}
h1,h2,h3 {
    color: white;
}
img {
    border-radius: 8px;
    transition: transform 0.3s ease;
}
img:hover {
    transform: scale(1.08);
}
</style>
""", unsafe_allow_html=True)

# ==================================
# SAFE REQUEST
# ==================================
def safe_request(url, params):
    try:
        r = requests.get(url, params=params)
        if r.status_code == 200:
            return r.json()
        return {}
    except:
        return {}

# ==================================
# API FUNCTIONS
# ==================================
def get_movies(endpoint):
    data = safe_request(f"{BASE_URL}{endpoint}", {"api_key": API_KEY})
    return data.get("results", [])

def get_movie_full(movie_id):
    return safe_request(
        f"{BASE_URL}/movie/{movie_id}",
        {"api_key": API_KEY, "append_to_response": "credits,videos"}
    )

def get_watch_providers(movie_id):
    data = safe_request(
        f"{BASE_URL}/movie/{movie_id}/watch/providers",
        {"api_key": API_KEY}
    )
    return data.get("results", {}).get("KE")

# ==================================
# CHECK IF MOVIE PAGE
# ==================================
query_params = st.query_params

if "movie_id" in query_params:

    movie_id = query_params["movie_id"]

    movie = get_movie_full(movie_id)

    if not movie:
        st.error("Movie not found.")
        st.stop()

    # BACK BUTTON
    if st.button("⬅ Back to Home"):
        st.query_params.clear()
        st.rerun()

    # BACKDROP
    if movie.get("backdrop_path"):
        st.image(BACKDROP_BASE + movie["backdrop_path"], use_container_width=True)

    st.title(movie.get("title"))

    col1, col2 = st.columns([1, 2])

    with col1:
        if movie.get("poster_path"):
            st.image(IMAGE_BASE + movie["poster_path"])

    with col2:
        st.write(movie.get("overview"))
        st.write(f"⭐ Rating: {movie.get('vote_average')}")
        st.write(f"📅 Release: {movie.get('release_date')}")
        st.write(f"⏱ Runtime: {movie.get('runtime')} mins")

    # TRAILER
    videos = movie.get("videos", {}).get("results", [])
    trailer = None
    for v in videos:
        if v.get("type") == "Trailer" and v.get("site") == "YouTube":
            trailer = v.get("key")
            break

    if trailer:
        st.subheader("🎬 Trailer")
        st.video(f"https://www.youtube.com/watch?v={trailer}")

    # ACTORS WITH PICTURES
    cast = movie.get("credits", {}).get("cast", [])[:8]

    if cast:
        st.subheader("🎭 Cast")
        cols = st.columns(len(cast))
        for i, actor in enumerate(cast):
            with cols[i]:
                if actor.get("profile_path"):
                    st.image(IMAGE_BASE + actor["profile_path"])
                st.caption(actor.get("name"))

    # WATCH PROVIDERS
    providers = get_watch_providers(movie_id)

    st.subheader("📺 Available in Kenya 🇰🇪")

    if providers and "flatrate" in providers:
        cols = st.columns(len(providers["flatrate"]))
        for i, p in enumerate(providers["flatrate"]):
            with cols[i]:
                if p.get("logo_path"):
                    st.image(LOGO_BASE + p["logo_path"])
                if providers.get("link"):
                    st.markdown(f"[Watch Now]({providers['link']})")
    else:
        st.warning("Not available in Kenya.")

# ==================================
# HOME PAGE
# ==================================
else:

    st.title("🎬 Creepy - Kenya Movie Discovery")

    def display_row(title, endpoint):
        st.subheader(title)
        movies = get_movies(endpoint)
        cols = st.columns(6)

        for i, movie in enumerate(movies[:18]):
            if movie.get("poster_path"):
                with cols[i % 6]:
                    st.markdown(
                        f"""
                        <a href="?movie_id={movie['id']}">
                            <img src="{IMAGE_BASE + movie['poster_path']}" width="100%">
                        </a>
                        """,
                        unsafe_allow_html=True
                    )

    # Infinite Scroll Feel (Load More Button)
    display_row("🔥 Popular", "/movie/popular")
    display_row("💥 Action", "/discover/movie?with_genres=28")
    display_row("😂 Comedy", "/discover/movie?with_genres=35")
    display_row("👻 Horror", "/discover/movie?with_genres=27")
