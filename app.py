import streamlit as st
import requests

# ==============================
# CONFIG
# ==============================
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"
IMG_URL = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="Creepy-Movie Recommendation", layout="wide")

# ==============================
# DARK NETFLIX STYLE
# ==============================
st.markdown("""
<style>
body { background-color: #0e0e0e; color: white; }
.movie-card img {
    border-radius: 10px;
    transition: transform 0.3s ease;
}
.movie-card img:hover {
    transform: scale(1.08);
}
</style>
""", unsafe_allow_html=True)

# ==============================
# SESSION STATE PAGE CONTROL
# ==============================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

# ==============================
# API FUNCTIONS (SAFE)
# ==============================
def safe_get(url, params):
    response = requests.get(url, params=params)
    data = response.json()
    return data

def search_movies(query):
    url = f"{BASE_URL}/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": query}
    data = safe_get(url, params)
    return data.get("results", [])

def get_popular_movies():
    url = f"{BASE_URL}/movie/popular"
    params = {"api_key": TMDB_API_KEY}
    data = safe_get(url, params)
    return data.get("results", [])

def get_movies_by_genre(genre_id):
    url = f"{BASE_URL}/discover/movie"
    params = {"api_key": TMDB_API_KEY, "with_genres": genre_id}
    data = safe_get(url, params)
    return data.get("results", [])

def get_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {"api_key": TMDB_API_KEY}
    return safe_get(url, params)

def get_movie_credits(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/credits"
    params = {"api_key": TMDB_API_KEY}
    return safe_get(url, params)

def get_movie_videos(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/videos"
    params = {"api_key": TMDB_API_KEY}
    return safe_get(url, params)

def get_watch_providers(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/watch/providers"
    params = {"api_key": TMDB_API_KEY}
    return safe_get(url, params)

# ==============================
# HOME PAGE
# ==============================
if st.session_state.page == "home":

    st.title("🎬 Creepy-Movie Recommendation")

    # Search Section
    search_query = st.text_input("Search for a movie")
    if st.button("Search"):
        results = search_movies(search_query)
        if results:
            st.subheader("Search Results")
            cols = st.columns(5)
            for i, movie in enumerate(results[:10]):
                with cols[i % 5]:
                    if movie.get("poster_path"):
                        if st.button(
                            "",
                            key=f"search_{movie['id']}"
                        ):
                            st.session_state.selected_movie = movie["id"]
                            st.session_state.page = "details"
                            st.rerun()

                        st.image(IMG_URL + movie["poster_path"])
        else:
            st.warning("No movie found.")

    # Popular Movies
    st.subheader("🔥 Popular")
    popular = get_popular_movies()
    cols = st.columns(6)
    for i, movie in enumerate(popular[:12]):
        with cols[i % 6]:
            if movie.get("poster_path"):
                if st.button("", key=f"pop_{movie['id']}"):
                    st.session_state.selected_movie = movie["id"]
                    st.session_state.page = "details"
                    st.rerun()
                st.image(IMG_URL + movie["poster_path"])

    # Action Genre
    st.subheader("💥 Action")
    action = get_movies_by_genre(28)
    cols = st.columns(6)
    for i, movie in enumerate(action[:12]):
        with cols[i % 6]:
            if movie.get("poster_path"):
                if st.button("", key=f"act_{movie['id']}"):
                    st.session_state.selected_movie = movie["id"]
                    st.session_state.page = "details"
                    st.rerun()
                st.image(IMG_URL + movie["poster_path"])


# ==============================
# DETAILS PAGE (Same Tab)
# ==============================
if st.session_state.page == "details":

    movie_id = st.session_state.selected_movie

    if st.button("⬅ Back"):
        st.session_state.page = "home"
        st.rerun()

    details = get_movie_details(movie_id)
    credits = get_movie_credits(movie_id)
    videos = get_movie_videos(movie_id)
    providers = get_watch_providers(movie_id)

    st.title(details.get("title", "Movie"))

    col1, col2 = st.columns([1, 2])

    with col1:
        if details.get("poster_path"):
            st.image(IMG_URL + details["poster_path"])

    with col2:
        st.write("⭐ Rating:", details.get("vote_average"))
        st.write("📅 Release:", details.get("release_date"))
        st.write(details.get("overview"))

    # Trailer
    st.subheader("🎬 Trailer")
    trailer_key = None
    for video in videos.get("results", []):
        if video["type"] == "Trailer" and video["site"] == "YouTube":
            trailer_key = video["key"]
            break

    if trailer_key:
        st.video(f"https://www.youtube.com/watch?v={trailer_key}")
    else:
        st.info("Trailer not available.")

    # Cast
    st.subheader("🎭 Top Cast")
    cast = credits.get("cast", [])[:6]
    cols = st.columns(6)
    for i, actor in enumerate(cast):
        with cols[i]:
            if actor.get("profile_path"):
                st.image(IMG_URL + actor["profile_path"])
            st.caption(actor["name"])

    # Watch Providers (Kenya)
    st.subheader("📺 Available In Kenya")
    kenya = providers.get("results", {}).get("KE")

    if kenya and "flatrate" in kenya:
        cols = st.columns(len(kenya["flatrate"]))
        for i, provider in enumerate(kenya["flatrate"]):
            with cols[i]:
                st.image("https://image.tmdb.org/t/p/w200" + provider["logo_path"])
                link = kenya.get("link")
                if link:
                    st.markdown(f"[Watch Now]({link})")
    else:
        st.info("Not available on major streaming platforms in Kenya.")
