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
# NETFLIX DARK UI + MOBILE
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #0e0e0e;
    color: white;
}
h1,h2,h3,h4,h5,h6,p,span,label {
    color: white !important;
}
img {
    border-radius: 10px;
    transition: transform 0.3s;
}
img:hover {
    transform: scale(1.05);
}
div.stButton > button {
    background-color: #e50914;
    color: white;
    border-radius: 6px;
    border: none;
}
div.stButton > button:hover {
    background-color: #b20710;
    color: white;
}
@media (max-width: 768px) {
    img {
        width: 100% !important;
    }
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 Creepy Movie Recommendation")

# =========================
# API FUNCTIONS
# =========================
def safe_request(url, params):
    try:
        res = requests.get(url, params=params)
        data = res.json()
        return data
    except:
        return {}

def get_movies(endpoint):
    data = safe_request(f"{BASE_URL}{endpoint}", {"api_key": TMDB_API_KEY})
    return data.get("results", [])

def search_movies(query):
    data = safe_request(f"{BASE_URL}/search/movie",
                        {"api_key": TMDB_API_KEY, "query": query})
    return data.get("results", [])

def get_movie_details(movie_id):
    return safe_request(f"{BASE_URL}/movie/{movie_id}",
                        {"api_key": TMDB_API_KEY})

def get_trailer(movie_id):
    data = safe_request(f"{BASE_URL}/movie/{movie_id}/videos",
                        {"api_key": TMDB_API_KEY})
    for vid in data.get("results", []):
        if vid.get("type") == "Trailer" and vid.get("site") == "YouTube":
            return f"https://www.youtube.com/embed/{vid['key']}"
    return None

def get_actors(movie_id):
    data = safe_request(f"{BASE_URL}/movie/{movie_id}/credits",
                        {"api_key": TMDB_API_KEY})
    return data.get("cast", [])[:6]

def get_watch_providers(movie_id):
    data = safe_request(f"{BASE_URL}/movie/{movie_id}/watch/providers",
                        {"api_key": TMDB_API_KEY})
    return data.get("results", {}).get("KE", {})

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

                # unique key fix
                unique_key = f"{title}_{movie['id']}"

                if st.button("View Details", key=unique_key):
                    st.session_state.selected_id = movie["id"]
                    st.rerun()

# =========================
# MAIN PAGE
# =========================
if "selected_id" not in st.session_state:

    query = st.text_input("Search movies...")

    if query:
        results = search_movies(query)
        if results:
            display_row("Search Results", results)
        else:
            st.warning("No movies found.")
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

    st.button("⬅ Back Home", key="back_home",
              on_click=lambda: st.session_state.pop("selected_id"))

    st.divider()

    col1, col2 = st.columns([1, 2])

    with col1:
        if movie.get("poster_path"):
            st.image(IMAGE_URL + movie["poster_path"])

    with col2:
        st.header(movie.get("title", "Unknown"))
        st.write(f"⭐ Rating: {movie.get('vote_average', 'N/A')}")
        st.write(f"📅 Release: {movie.get('release_date', 'N/A')}")
        st.write(movie.get("overview", "No description available."))

    # Trailer
    trailer = get_trailer(movie_id)
    if trailer:
        st.subheader("▶ Trailer")
        st.markdown(
            f'<iframe width="100%" height="400" src="{trailer}" frameborder="0" allowfullscreen></iframe>',
            unsafe_allow_html=True
        )

    # Actors
    cast = get_actors(movie_id)
    if cast:
        st.subheader("🎭 Top Cast")
        cols = st.columns(len(cast))
        for i, actor in enumerate(cast):
            with cols[i]:
                if actor.get("profile_path"):
                    st.image(IMAGE_URL + actor["profile_path"])
                st.caption(actor.get("name"))

    # Watch Providers
    providers = get_watch_providers(movie_id)

    st.subheader("📺 Available in Kenya")

    if providers:

        if providers.get("flatrate"):
            st.write("Streaming")
            cols = st.columns(len(providers["flatrate"]))
            for i, p in enumerate(providers["flatrate"]):
                with cols[i]:
                    if p.get("logo_path"):
                        st.image(LOGO_URL + p["logo_path"])
            if providers.get("link"):
                st.markdown(f"[Watch Now]({providers['link']})")

        if providers.get("rent"):
            st.write("Rent")
            cols = st.columns(len(providers["rent"]))
            for i, p in enumerate(providers["rent"]):
                with cols[i]:
                    if p.get("logo_path"):
                        st.image(LOGO_URL + p["logo_path"])
            if providers.get("link"):
                st.markdown(f"[Watch Now]({providers['link']})")

        if providers.get("buy"):
            st.write("Buy")
            cols = st.columns(len(providers["buy"]))
            for i, p in enumerate(providers["buy"]):
                with cols[i]:
                    if p.get("logo_path"):
                        st.image(LOGO_URL + p["logo_path"])
            if providers.get("link"):
                st.markdown(f"[Watch Now]({providers['link']})")

    else:
        st.warning("❌ Not available in Kenya.")
