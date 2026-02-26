import streamlit as st
import requests

# ==============================
# ✅ PWA + MOBILE META (ADDED)
# ==============================

st.markdown("""
<link rel="manifest" href="/static/manifest.json">
<meta name="theme-color" content="#E50914">
<link rel="apple-touch-icon" href="/static/icon-192.png">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
""", unsafe_allow_html=True)

# ==============================
# SETTINGS
# ==============================

API_KEY = "YOUR_TMDB_API_KEY"
BASE_URL = "https://api.themoviedb.org/3"
IMG_URL = "https://image.tmdb.org/t/p/w500"

st.set_page_config(layout="wide", page_title="Creepy Movies")

# ==============================
# FUNCTIONS
# ==============================

def search_movies(query):
    url = f"{BASE_URL}/search/movie?api_key={API_KEY}&query={query}"
    return requests.get(url).json().get("results", [])

def get_popular():
    url = f"{BASE_URL}/movie/popular?api_key={API_KEY}"
    return requests.get(url).json().get("results", [])

def get_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&append_to_response=credits,videos"
    return requests.get(url).json()

def get_watch_providers(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/watch/providers?api_key={API_KEY}"
    data = requests.get(url).json()
    return data.get("results", {}).get("KE", {})  # Kenya region

# ==============================
# SESSION STATE
# ==============================

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

# ==============================
# DARK NETFLIX STYLE
# ==============================

st.markdown("""
<style>
body {background-color: #000000;}
h1, h2, h3, p {color: white;}

.movie-card {
    text-align:center;
}
.red-btn {
    background-color:#E50914;
    color:white;
    padding:8px 16px;
    border:none;
    border-radius:5px;
    text-decoration:none;
    font-weight:bold;
}
.red-btn:hover {
    background-color:#b20710;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# HOME PAGE
# ==============================

if st.session_state.selected_movie is None:

    st.title("🎬 Creepy Movie Recommendation")

    # Search
    query = st.text_input("Search for a movie")

    if query:
        movies = search_movies(query)
    else:
        movies = get_popular()

    cols = st.columns(4)

    for index, movie in enumerate(movies):
        if movie.get("poster_path"):
            with cols[index % 4]:
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)

                # Clickable Poster
                if st.button("", key=movie["id"]):
                    st.session_state.selected_movie = movie["id"]
                    st.rerun()

                st.image(IMG_URL + movie["poster_path"])

                # View Details Button (Red)
                if st.button("View Details", key=f"view_{movie['id']}"):
                    st.session_state.selected_movie = movie["id"]
                    st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# DETAILS PAGE (Same Tab)
# ==============================

else:

    movie_id = st.session_state.selected_movie
    details = get_movie_details(movie_id)
    providers = get_watch_providers(movie_id)

    # Back Home Button (Red)
    if st.button("⬅ Back Home"):
        st.session_state.selected_movie = None
        st.rerun()

    st.title(details.get("title"))

    col1, col2 = st.columns([1,2])

    with col1:
        if details.get("poster_path"):
            st.image(IMG_URL + details["poster_path"])

    with col2:
        st.write(details.get("overview"))
        st.write("⭐ Rating:", details.get("vote_average"))

    # ==========================
    # ACTORS
    # ==========================

    st.subheader("Cast")

    cast = details.get("credits", {}).get("cast", [])[:6]
    cast_cols = st.columns(6)

    for i, actor in enumerate(cast):
        with cast_cols[i]:
            if actor.get("profile_path"):
                st.image("https://image.tmdb.org/t/p/w200" + actor["profile_path"])
            st.write(actor.get("name"))

    # ==========================
    # TRAILER
    # ==========================

    st.subheader("Trailer")

    videos = details.get("videos", {}).get("results", [])
    for video in videos:
        if video["type"] == "Trailer" and video["site"] == "YouTube":
            st.video(f"https://www.youtube.com/watch?v={video['key']}")
            break

    # ==========================
    # WATCH PROVIDERS
    # ==========================

    st.subheader("Available On")

    if providers:
        for provider_type in ["flatrate", "free", "ads", "rent", "buy"]:
            if provider_type in providers:
                st.write(f"### {provider_type.capitalize()}")
                prov_cols = st.columns(6)

                for i, provider in enumerate(providers[provider_type]):
                    with prov_cols[i % 6]:
                        logo = "https://image.tmdb.org/t/p/w200" + provider["logo_path"]
                        st.image(logo, width=80)
                        st.write(provider["provider_name"])
                        if "link" in providers:
                            st.markdown(
                                f'<a href="{providers["link"]}" target="_blank" class="red-btn">Watch Now</a>',
                                unsafe_allow_html=True
                            )
    else:
        st.info("No streaming information available in your region.")
