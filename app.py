import streamlit as st
import requests

# ==============================
# CONFIG
# ==============================
st.set_page_config(page_title="Kenya Movie Discovery Engine", layout="wide")

API_KEY = "YOUR_TMDB_API_KEY"
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# ==============================
# SESSION STATE
# ==============================
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

# ==============================
# FUNCTIONS
# ==============================

def get_popular_movies():
    url = f"{BASE_URL}/movie/popular"
    params = {"api_key": API_KEY}
    return requests.get(url, params=params).json()["results"]

def get_movies_by_genre(genre_id):
    url = f"{BASE_URL}/discover/movie"
    params = {
        "api_key": API_KEY,
        "with_genres": genre_id
    }
    return requests.get(url, params=params).json()["results"]

def get_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": API_KEY,
        "append_to_response": "credits,videos"
    }
    return requests.get(url, params=params).json()

def get_watch_providers(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/watch/providers"
    params = {"api_key": API_KEY}
    data = requests.get(url, params=params).json()
    
    if "results" in data and "KE" in data["results"]:
        return data["results"]["KE"]
    return None

# ==============================
# UI HEADER
# ==============================

st.title("🎬 Kenya’s Movie Discovery Engine")
st.write("Find where to watch movies in Kenya 🇰🇪")

# ==============================
# POPULAR MOVIES
# ==============================

st.header("🔥 Popular Movies")

popular_movies = get_popular_movies()

cols = st.columns(5)

for i, movie in enumerate(popular_movies[:10]):
    with cols[i % 5]:
        if movie["poster_path"]:
            st.image(IMAGE_BASE + movie["poster_path"])
        
        if st.button(movie["title"], key=f"popular_{movie['id']}"):
            st.session_state.selected_movie = movie["id"]

# ==============================
# GENRE SECTIONS
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
            if movie["poster_path"]:
                st.image(IMAGE_BASE + movie["poster_path"])
            
            if st.button(movie["title"], key=f"{genre_id}_{movie['id']}"):
                st.session_state.selected_movie = movie["id"]

# ==============================
# MOVIE DETAILS SECTION
# ==============================

if st.session_state.selected_movie:

    details = get_movie_details(st.session_state.selected_movie)

    st.divider()
    st.header(details["title"])

    col1, col2 = st.columns([1, 2])

    with col1:
        if details["poster_path"]:
            st.image(IMAGE_BASE + details["poster_path"])

    with col2:
        st.write(details["overview"])
        st.write(f"⭐ Rating: {details['vote_average']}")
        st.write(f"⏱ Runtime: {details.get('runtime', 'N/A')} minutes")

    # ==============================
    # CAST
    # ==============================

    st.subheader("🎭 Top Cast")

    cast = details["credits"]["cast"][:5]

    for actor in cast:
        st.write(f"{actor['name']} as {actor['character']}")

    # ==============================
    # TRAILER
    # ==============================

    st.subheader("🎬 Trailer")

    videos = details["videos"]["results"]
    trailer_key = None

    for video in videos:
        if video["type"] == "Trailer" and video["site"] == "YouTube":
            trailer_key = video["key"]
            break

    if trailer_key:
        st.video(f"https://www.youtube.com/watch?v={trailer_key}")
    else:
        st.info("Trailer not available.")

    # ==============================
    # WATCH PROVIDERS (KENYA)
    # ==============================

    st.subheader("📺 Where to Watch in Kenya 🇰🇪")

    providers = get_watch_providers(st.session_state.selected_movie)

    if providers:

        if "flatrate" in providers:
            for provider in providers["flatrate"]:
                logo = provider["logo_path"]
                name = provider["provider_name"]

                st.image("https://image.tmdb.org/t/p/w200" + logo, width=100)
                st.markdown(
                    f"[▶ Watch on {name}]({providers.get('link', '#')})",
                    unsafe_allow_html=True
                )

    else:
        st.warning("Not available on streaming platforms in Kenya.")

    # ==============================
    # CLOSE BUTTON
    # ==============================

    if st.button("❌ Close"):
        st.session_state.selected_movie = None
