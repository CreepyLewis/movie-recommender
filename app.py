import streamlit as st
import requests

# =========================
# CONFIG
# =========================
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_URL = "https://image.tmdb.org/t/p/w500"
LOGO_URL = "https://image.tmdb.org/t/p/w200"

st.set_page_config(page_title="Creepy Movie Recommendation", layout="wide")

# =========================
# DEVICE DETECTION (Mobile Only CSS)
# =========================
st.markdown("""
<style>
/* Default desktop styling (unchanged) */
.stApp {
    background-color: #0e0e0e;
    color: white;
}
h1,h2,h3,h4 {
    color: white;
}
img {
    border-radius: 10px;
    transition: transform 0.3s;
}
img:hover {
    transform: scale(1.08);
    cursor: pointer;
}

/* Red Buttons */
div.stButton > button {
    background-color: #e50914;
    color: white;
    border: none;
    border-radius: 6px;
}
div.stButton > button:hover {
    background-color: #ff1e2d;
}

/* 📱 MOBILE ONLY */
@media (max-width: 768px) {

    h1 {
        font-size: 22px !important;
    }

    h2 {
        font-size: 18px !important;
    }

    .stButton > button {
        width: 100%;
        font-size: 14px;
    }

    img {
        border-radius: 6px;
    }

}
</style>
""", unsafe_allow_html=True)

st.title("🎬 Creepy Movie Recommendation")

# =========================
# API FUNCTIONS
# =========================
def safe_get(url, params):
    try:
        r = requests.get(url, params=params)
        return r.json()
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

def get_watch_providers(movie_id):
    data = safe_get(f"{BASE_URL}/movie/{movie_id}/watch/providers",
                    {"api_key": TMDB_API_KEY})
    return data.get("results", {}).get("KE", {})

def get_actors(movie_id):
    data = safe_get(f"{BASE_URL}/movie/{movie_id}/credits",
                    {"api_key": TMDB_API_KEY})
    return data.get("cast", [])[:6]

# =========================
# DISPLAY ROW
# =========================
def display_row(title, movies):
    st.subheader(title)
    cols = st.columns(6)

    for i, movie in enumerate(movies[:12]):
        poster = movie.get("poster_path")
        if poster:
            with cols[i % 6]:
                st.image(IMAGE_URL + poster)
                if st.button("View Details", key=f"view_{movie['id']}"):
                    st.session_state.selected_id = movie["id"]
                    st.rerun()

# =========================
# MAIN NAVIGATION
# =========================
if "selected_id" not in st.session_state:

    query = st.text_input("🔍 Search movies")

    if query:
        results = search_movies(query)
        display_row("Search Results", results)
    else:
        popular = get_movies("/movie/popular")
        action = get_movies("/discover/movie?with_genres=28")
        comedy = get_movies("/discover/movie?with_genres=35")
        horror = get_movies("/discover/movie?with_genres=27")
        romance = get_movies("/discover/movie?with_genres=10749")

        display_row("🔥 Popular Now", popular)
        display_row("💥 Action", action)
        display_row("😂 Comedy", comedy)
        display_row("👻 Horror", horror)
        display_row("❤️ Romance", romance)

# =========================
# MOVIE DETAILS PAGE
# =========================
else:

    movie_id = st.session_state.selected_id
    movie = get_movie_details(movie_id)

    if st.button("⬅ Back Home"):
        del st.session_state.selected_id
        st.rerun()

    st.divider()
    st.header(movie.get("title", "Unknown"))

    col1, col2 = st.columns([1, 2])

    with col1:
        if movie.get("poster_path"):
            st.image(IMAGE_URL + movie["poster_path"])

    with col2:
        st.write(f"⭐ Rating: {movie.get('vote_average', 'N/A')}")
        st.write(f"📅 Release: {movie.get('release_date', 'N/A')}")
        st.write(movie.get("overview", "No description available."))

    # Trailer
    trailer = get_trailer(movie_id)
    if trailer:
        st.markdown("### ▶ Trailer")
        st.markdown(
            f'<iframe width="100%" height="400" src="{trailer}" frameborder="0" allowfullscreen></iframe>',
            unsafe_allow_html=True
        )

    # Actors
    actors = get_actors(movie_id)
    if actors:
        st.markdown("### 🎭 Top Cast")
        cols = st.columns(len(actors))
        for i, actor in enumerate(actors):
            with cols[i]:
                if actor.get("profile_path"):
                    st.image(IMAGE_URL + actor["profile_path"])
                st.caption(actor.get("name", ""))

    # Providers
    providers = get_watch_providers(movie_id)
    st.markdown("### 📺 Available in Kenya")

    if providers:
        for category in ["flatrate", "rent", "buy"]:
            if category in providers:
                cols = st.columns(len(providers[category]))
                for i, p in enumerate(providers[category]):
                    with cols[i]:
                        if p.get("logo_path"):
                            st.image(LOGO_URL + p["logo_path"])
                        if providers.get("link"):
                            st.markdown(
                                f"[Watch Now]({providers['link']})",
                                unsafe_allow_html=True
                            )
    else:
        st.warning("Not available in Kenya.")
