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
</style>
""", unsafe_allow_html=True)

st.title("🎬 Creepy Movie Recommendation")

# =========================
# SYNC QUERY PARAMS TO SESSION
# =========================
query_params = st.experimental_get_query_params()
if "movie_id" in query_params:
    st.session_state.selected_id = int(query_params["movie_id"])

# =========================
# API FUNCTIONS
# =========================
def get_movies(endpoint):
    url = f"{BASE_URL}{endpoint}"
    params = {"api_key": TMDB_API_KEY}
    res = requests.get(url, params=params)
    return res.json().get("results", [])

def search_movies(query):
    url = f"{BASE_URL}/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": query}
    res = requests.get(url, params=params)
    return res.json().get("results", [])

def get_trailer(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/videos"
    res = requests.get(url, params={"api_key": TMDB_API_KEY})
    for vid in res.json().get("results", []):
        if vid["type"] == "Trailer" and vid["site"] == "YouTube":
            return f"https://www.youtube.com/embed/{vid['key']}"
    return None

def get_watch_providers(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/watch/providers"
    res = requests.get(url, params={"api_key": TMDB_API_KEY})
    data = res.json().get("results", {})
    return data.get("KE")

def get_actors(movie_id, limit=6):
    url = f"{BASE_URL}/movie/{movie_id}/credits"
    res = requests.get(url, params={"api_key": TMDB_API_KEY})
    cast = res.json().get("cast", [])
    return cast[:limit]  # top actors

# =========================
# DISPLAY ROW FUNCTION
# =========================
def display_row(title, movies):
    st.subheader(title)
    n_cols = min(6, len(movies))
    cols = st.columns(n_cols)

    for i, movie in enumerate(movies[:12]):
        if movie.get("poster_path"):
            poster_url = IMAGE_URL + movie["poster_path"]
            with cols[i % n_cols]:
                # Clickable poster via JS (same tab)
                st.markdown(
                    f"""
                    <div style="cursor:pointer;" onclick="
                        window.location.href='?movie_id={movie['id']}';
                    ">
                        <img src="{poster_url}" width="100%" 
                             style="border-radius:10px; transition: transform 0.3s;" 
                             onmouseover="this.style.transform='scale(1.08)';" 
                             onmouseout="this.style.transform='scale(1)';">
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# =========================
# SEARCH BAR
# =========================
query = st.text_input("Search movies...")

if query:
    movies = search_movies(query)
    if movies:
        display_row("Search Results", movies)
    else:
        st.warning("No movies found.")
else:
    # =========================
    # NETFLIX STYLE ROWS
    # =========================
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
# MOVIE DETAILS SECTION
# =========================
if "selected_id" in st.session_state:
    movie_id = st.session_state.selected_id

    # Fetch movie details
    movie = requests.get(f"{BASE_URL}/movie/{movie_id}", params={"api_key": TMDB_API_KEY}).json()
    st.divider()
    st.subheader(movie["title"])
    st.write(f"⭐ Rating: {movie['vote_average']}")
    st.write(f"📅 Release: {movie['release_date']}")
    st.write(movie["overview"])

    # 🎬 Trailer
    trailer = get_trailer(movie_id)
    if trailer:
        st.markdown("### ▶ Trailer")
        st.markdown(
            f"""
            <iframe width="100%" height="400" src="{trailer}" frameborder="0" allowfullscreen></iframe>
            """,
            unsafe_allow_html=True
        )

    # 🎭 Actors
    cast = get_actors(movie_id)
    if cast:
        st.markdown("### 🎭 Top Cast")
        cols = st.columns(len(cast))
        for i, actor in enumerate(cast):
            with cols[i]:
                if actor.get("profile_path"):
                    st.image(IMAGE_URL + actor["profile_path"])
                st.write(actor["name"])

    # 📺 Watch Providers
    providers = get_watch_providers(movie_id)
    if providers:
        st.markdown("### 📺 Available in Kenya")

        if "flatrate" in providers:
            st.write("Streaming:")
            cols = st.columns(len(providers["flatrate"]))
            for i, p in enumerate(providers["flatrate"]):
                with cols[i]:
                    st.image(LOGO_URL + p["logo_path"])
                    if providers.get("link"):
                        st.markdown(f"[Watch Now]({providers['link']})")

        if "rent" in providers:
            st.write("Rent:")
            cols = st.columns(len(providers["rent"]))
            for i, p in enumerate(providers["rent"]):
                with cols[i]:
                    st.image(LOGO_URL + p["logo_path"])
                    if providers.get("link"):
                        st.markdown(f"[Watch Now]({providers['link']})")
    else:
        st.write("❌ Not available in Kenya.")
