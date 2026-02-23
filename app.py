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
if "movie_id" in query_params and query_params["movie_id"]:
    try:
        st.session_state.selected_id = int(query_params["movie_id"][0])
    except ValueError:
        pass

# =========================
# API FUNCTIONS
# =========================
def get_movies(endpoint):
    res = requests.get(f"{BASE_URL}{endpoint}", params={"api_key": TMDB_API_KEY})
    return res.json().get("results", [])

def search_movies(query):
    res = requests.get(f"{BASE_URL}/search/movie", params={"api_key": TMDB_API_KEY, "query": query})
    return res.json().get("results", [])

def get_trailer(movie_id):
    res = requests.get(f"{BASE_URL}/movie/{movie_id}/videos", params={"api_key": TMDB_API_KEY})
    for vid in res.json().get("results", []):
        if vid.get("type") == "Trailer" and vid.get("site") == "YouTube":
            return f"https://www.youtube.com/embed/{vid['key']}"
    return None

def get_watch_providers(movie_id):
    res = requests.get(f"{BASE_URL}/movie/{movie_id}/watch/providers", params={"api_key": TMDB_API_KEY})
    return res.json().get("results", {}).get("KE", {})

def get_actors(movie_id, limit=6):
    res = requests.get(f"{BASE_URL}/movie/{movie_id}/credits", params={"api_key": TMDB_API_KEY})
    cast = res.json().get("cast", [])
    return cast[:limit] if cast else []

# =========================
# DISPLAY ROW FUNCTION
# =========================
def display_row(title, movies):
    st.subheader(title)
    n_cols = min(6, len(movies))
    if n_cols == 0:
        return
    cols = st.columns(n_cols)

    for i, movie in enumerate(movies[:12]):
        poster_path = movie.get("poster_path")
        if poster_path:
            poster_url = IMAGE_URL + poster_path
            with cols[i % n_cols]:
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

    # Movie details
    movie = requests.get(f"{BASE_URL}/movie/{movie_id}", params={"api_key": TMDB_API_KEY}).json()
    st.divider()
    st.subheader(movie.get("title", "Unknown Title"))
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
    cast = get_actors(movie_id)
    if cast:
        st.markdown("### 🎭 Top Cast")
        n_cols = len(cast)
        cols = st.columns(n_cols if n_cols > 0 else 1)
        for i, actor in enumerate(cast):
            with cols[i % n_cols]:
                profile_path = actor.get("profile_path")
                if profile_path:
                    st.image(IMAGE_URL + profile_path)
                st.write(actor.get("name", "Unknown"))

    # Watch Providers
    providers = get_watch_providers(movie_id)
    if providers:
        st.markdown("### 📺 Available in Kenya")

        if "flatrate" in providers:
            st.write("Streaming:")
            cols = st.columns(len(providers["flatrate"]))
            for i, p in enumerate(providers["flatrate"]):
                with cols[i % len(providers["flatrate"])]:
                    logo = p.get("logo_path")
                    if logo:
                        st.image(LOGO_URL + logo)
                    if providers.get("link"):
                        st.markdown(f"[Watch Now]({providers['link']})")

        if "rent" in providers:
            st.write("Rent:")
            cols = st.columns(len(providers["rent"]))
            for i, p in enumerate(providers["rent"]):
                with cols[i % len(providers["rent"])]:
                    logo = p.get("logo_path")
                    if logo:
                        st.image(LOGO_URL + logo)
                    if providers.get("link"):
                        st.markdown(f"[Watch Now]({providers['link']})")
    else:
        st.write("❌ Not available in Kenya.")
