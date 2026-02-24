import streamlit as st
import requests

# ==============================
# CONFIG
# ==============================
st.set_page_config(page_title="Creepy - Kenya Movie Discovery", layout="wide")

try:
    API_KEY = st.secrets["TMDB_API_KEY"]
except:
    st.error("TMDB API Key not found. Add it in Streamlit secrets.")
    st.stop()

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
LOGO_BASE = "https://image.tmdb.org/t/p/w200"

# ==============================
# SESSION STATE
# ==============================
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

# ==============================
# SAFE API FUNCTIONS
# ==============================

def safe_request(url, params):
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("TMDB API Error. Check your API key.")
            return {}
    except:
        st.error("Network error connecting to TMDB.")
        return {}

def get_popular_movies():
    data = safe_request(f"{BASE_URL}/movie/popular", {"api_key": API_KEY})
    return data.get("results", [])

def get_movies_by_genre(genre_id):
    data = safe_request(
        f"{BASE_URL}/discover/movie",
        {"api_key": API_KEY, "with_genres": genre_id}
    )
    return data.get("results", [])

def get_movie_details(movie_id):
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

# ==============================
# UI HEADER
# ==============================

st.title("🎬 Creepy - Kenya’s Movie Discovery Engine 🇰🇪")
st.write("Find where to watch movies in Kenya")

# ==============================
# POPULAR MOVIES
# ==============================

st.header("🔥 Popular Movies")

popular_movies = get_popular_movies()

cols = st.columns(5)

for i, movie in enumerate(popular_movies[:10]):
    with cols[i % 5]:
        if movie.get("poster_path"):
            st.image(IMAGE_BASE + movie["poster_path"])
        if st.button(movie.get("title", "Unknown"), key=f"popular_{movie['id']}"):
            st.session_state.selected_movie = movie["id"]

# ==============================
# GENRES
# ==============================

genres = {
    "Action 💥": 28,
    "Comedy 😂": 35,
    "Horror 👻": 27,
    "Romance ❤️": 10749
}

for genre_name, genre_id in genres.items():
    st.header(genre_name)
    movies = get_movies_by_genre(genre_id)
    cols = st.columns(5)

    for i, movie in enumerate(movies[:5]):
        with cols[i % 5]:
            if movie.get("poster_path"):
                st.image(IMAGE_BASE + movie["poster_path"])
            if st.button(movie.get("title", "Unknown"), key=f"{genre_id}_{movie['id']}"):
                st.session_state.selected_movie = movie["id"]

# ==============================
# MOVIE DETAILS
# ==============================

if st.session_state.selected_movie:

    details = get_movie_details(st.session_state.selected_movie)

    if not details:
        st.warning("Could not load movie details.")
    else:
        st.divider()
        st.header(details.get("title", "Unknown Title"))

        col1, col2 = st.columns([1, 2])

        with col1:
            if details.get("poster_path"):
                st.image(IMAGE_BASE + details["poster_path"])

        with col2:
            st.write(details.get("overview", "No description available."))
            st.write(f"⭐ Rating: {details.get('vote_average', 'N/A')}")
            st.write(f"⏱ Runtime: {details.get('runtime', 'N/A')} minutes")

        # ==============================
        # CAST
        # ==============================

        cast = details.get("credits", {}).get("cast", [])[:5]

        if cast:
            st.subheader("🎭 Top Cast")
            for actor in cast:
                st.write(f"{actor.get('name')} as {actor.get('character')}")

        # ==============================
        # TRAILER
        # ==============================

        videos = details.get("videos", {}).get("results", [])
        trailer_key = None

        for video in videos:
            if video.get("type") == "Trailer" and video.get("site") == "YouTube":
                trailer_key = video.get("key")
                break

        st.subheader("🎬 Trailer")

        if trailer_key:
            st.video(f"https://www.youtube.com/watch?v={trailer_key}")
        else:
            st.info("Trailer not available.")

        # ==============================
        # WATCH PROVIDERS (KENYA)
        # ==============================

        st.subheader("📺 Available in Kenya 🇰🇪")

        providers = get_watch_providers(st.session_state.selected_movie)

        if providers and "flatrate" in providers:
            for provider in providers["flatrate"]:
                if provider.get("logo_path"):
                    st.image(LOGO_BASE + provider["logo_path"], width=100)
                name = provider.get("provider_name")
                link = providers.get("link")
                if link:
                    st.markdown(f"[▶ Watch on {name}]({link})")
        else:
            st.warning("Not available on streaming platforms in Kenya.")

        # CLOSE BUTTON
        if st.button("❌ Close"):
            st.session_state.selected_movie = None
