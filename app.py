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
# DARK NETFLIX STYLE
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
img {
    border-radius: 10px;
    transition: transform 0.3s;
}
img:hover {
    transform: scale(1.08);
    cursor: pointer;
}
a {
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 Creepy Movie Recommendation")

# =========================
# QUERY PARAM HANDLING (FIXED)
# =========================
query_params = st.query_params

if "movie_id" in query_params:
    try:
        st.session_state.selected_id = int(query_params["movie_id"])
    except:
        pass

# =========================
# API FUNCTIONS
# =========================
def get_movies(endpoint):
    res = requests.get(f"{BASE_URL}{endpoint}", params={"api_key": TMDB_API_KEY})
    return res.json().get("results", [])

def search_movies(query):
    res = requests.get(f"{BASE_URL}/search/movie",
                       params={"api_key": TMDB_API_KEY, "query": query})
    return res.json().get("results", [])

def get_movie_details(movie_id):
    res = requests.get(f"{BASE_URL}/movie/{movie_id}",
                       params={"api_key": TMDB_API_KEY})
    return res.json()

def get_trailer(movie_id):
    res = requests.get(f"{BASE_URL}/movie/{movie_id}/videos",
                       params={"api_key": TMDB_API_KEY})
    for vid in res.json().get("results", []):
        if vid.get("type") == "Trailer" and vid.get("site") == "YouTube":
            return f"https://www.youtube.com/embed/{vid['key']}"
    return None

def get_watch_providers(movie_id):
    res = requests.get(f"{BASE_URL}/movie/{movie_id}/watch/providers",
                       params={"api_key": TMDB_API_KEY})
    return res.json().get("results", {}).get("KE", {})

def get_actors(movie_id, limit=6):
    res = requests.get(f"{BASE_URL}/movie/{movie_id}/credits",
                       params={"api_key": TMDB_API_KEY})
    return res.json().get("cast", [])[:limit]

# =========================
# DISPLAY ROW
# =========================
def display_row(title, movies):
    if not movies:
        return

    st.subheader(title)
    cols = st.columns(6)

    for i, movie in enumerate(movies[:12]):
        poster = movie.get("poster_path")
        if poster:
            with cols[i % 6]:
                st.markdown(
                    f"""
                    <a href="?movie_id={movie['id']}">
                        <img src="{IMAGE_URL + poster}" width="100%">
                    </a>
                    """,
                    unsafe_allow_html=True
                )
                st.caption(movie.get("title"))

# =========================
# SEARCH OR HOME
# =========================
query = st.text_input("🔍 Search movies...")

if query:
    results = search_movies(query)
    if results:
        display_row("Search Results", results)
    else:
        st.warning("No movies found.")
else:
    display_row("🔥 Popular Now", get_movies("/movie/popular"))
    display_row("💥 Action", get_movies("/discover/movie?with_genres=28"))
    display_row("😂 Comedy", get_movies("/discover/movie?with_genres=35"))
    display_row("👻 Horror", get_movies("/discover/movie?with_genres=27"))
    display_row("❤️ Romance", get_movies("/discover/movie?with_genres=10749"))

# =========================
# MOVIE DETAILS
# =========================
if "selected_id" in st.session_state:

    movie_id = st.session_state.selected_id
    movie = get_movie_details(movie_id)

    st.divider()
    st.header(movie.get("title", "Unknown Title"))

    col1, col2 = st.columns([1, 2])

    with col1:
        if movie.get("poster_path"):
            st.image(IMAGE_URL + movie["poster_path"])

    with col2:
        st.write(f"⭐ Rating: {movie.get('vote_average', 'N/A')}")
        st.write(f"📅 Release: {movie.get('release_date', 'N/A')}")
        st.write(movie.get("overview", "No description available."))

    # TRAILER
    trailer = get_trailer(movie_id)
    if trailer:
        st.markdown("### ▶ Trailer")
        st.markdown(
            f'<iframe width="100%" height="400" src="{trailer}" frameborder="0" allowfullscreen></iframe>',
            unsafe_allow_html=True
        )

    # CAST
    cast = get_actors(movie_id)
    if cast:
        st.markdown("### 🎭 Top Cast")
        cols = st.columns(len(cast))
        for i, actor in enumerate(cast):
            with cols[i]:
                if actor.get("profile_path"):
                    st.image(IMAGE_URL + actor["profile_path"])
                st.caption(actor.get("name"))

    # WATCH PROVIDERS (KENYA)
    providers = get_watch_providers(movie_id)

    if providers:
        st.markdown("### 📺 Available in Kenya")

        provider_types = ["flatrate", "rent", "buy"]

        for ptype in provider_types:
            if ptype in providers and providers[ptype]:

                st.markdown(f"**{ptype.capitalize()}**")
                cols = st.columns(len(providers[ptype]))

                for i, p in enumerate(providers[ptype]):
                    with cols[i]:
                        if p.get("logo_path"):
                            st.image(LOGO_URL + p["logo_path"])
                        if providers.get("link"):
                            st.markdown(
                                f"[Watch Now]({providers['link']})",
                                unsafe_allow_html=True
                            )
    else:
        st.write("❌ Not available in Kenya.")
