import streamlit as st
import requests

# ==============================
# 🔥 PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="Creepy Movie Recommendation",
    page_icon="🎬",
    layout="wide"
)

# ==============================
# 📱 PWA + MOBILE META
# ==============================
st.markdown("""
<link rel="manifest" href="/static/manifest.json">
<meta name="theme-color" content="#E50914">
<link rel="apple-touch-icon" href="/static/icon-192.png">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
""", unsafe_allow_html=True)

# ==============================
# 🎨 NETFLIX DARK UI
# ==============================
st.markdown("""
<style>
body {
    background-color: #000000;
}
.stApp {
    background-color: #000000;
}
h1, h2, h3, h4, h5, h6, p {
    color: white;
}
.movie-card {
    text-align: center;
}
.red-btn button {
    background-color: #E50914 !important;
    color: white !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# 🔑 TMDB API
# ==============================
API_KEY = "YOUR_TMDB_API_KEY"
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# ==============================
# 🎥 FUNCTIONS
# ==============================

def search_movies(query, page=1):
    url = f"{BASE_URL}/search/movie"
    params = {"api_key": API_KEY, "query": query, "page": page}
    return requests.get(url, params=params).json()

def get_popular(page=1):
    url = f"{BASE_URL}/movie/popular"
    params = {"api_key": API_KEY, "page": page}
    return requests.get(url, params=params).json()

def get_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {"api_key": API_KEY, "append_to_response": "videos,credits"}
    return requests.get(url, params=params).json()

def get_watch_providers(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/watch/providers"
    params = {"api_key": API_KEY}
    data = requests.get(url, params=params).json()
    return data.get("results", {}).get("KE")  # Kenya region

# ==============================
# 📂 SESSION STATE
# ==============================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "movie_id" not in st.session_state:
    st.session_state.movie_id = None

if "page_number" not in st.session_state:
    st.session_state.page_number = 1

# ==============================
# 🏠 HOME PAGE
# ==============================
if st.session_state.page == "home":

    st.title("🎬 Creepy Movie Recommendation")

    col1, col2 = st.columns([4,1])

    with col1:
        search_query = st.text_input("Search for a movie")

    with col2:
        search_btn = st.button("Search")

    if search_btn and search_query:
        data = search_movies(search_query)
    else:
        data = get_popular(st.session_state.page_number)

    movies = data.get("results", [])

    cols = st.columns(5)

    for index, movie in enumerate(movies):
        with cols[index % 5]:
            if movie.get("poster_path"):
                poster_url = IMAGE_BASE + movie["poster_path"]

                if st.button(" ", key=movie["id"]):
                    st.session_state.movie_id = movie["id"]
                    st.session_state.page = "details"
                    st.rerun()

                st.image(poster_url)
                st.markdown(f"**{movie['title']}**")

                if st.button("View Details", key=f"details_{movie['id']}"):
                    st.session_state.movie_id = movie["id"]
                    st.session_state.page = "details"
                    st.rerun()

    if st.button("Load More"):
        st.session_state.page_number += 1
        st.rerun()

# ==============================
# 🎬 DETAILS PAGE
# ==============================
if st.session_state.page == "details":

    movie_id = st.session_state.movie_id
    details = get_movie_details(movie_id)

    st.markdown("<div class='red-btn'>", unsafe_allow_html=True)
    if st.button("⬅ Back Home"):
        st.session_state.page = "home"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1,2])

    with col1:
        if details.get("poster_path"):
            st.image(IMAGE_BASE + details["poster_path"])

    with col2:
        st.header(details.get("title"))
        st.write(details.get("overview"))
        st.write(f"⭐ Rating: {details.get('vote_average')}")

    # 🎥 Trailer
    st.subheader("🎥 Trailer")
    videos = details.get("videos", {}).get("results", [])
    trailer = next((v for v in videos if v["type"] == "Trailer"), None)

    if trailer:
        youtube_url = f"https://www.youtube.com/watch?v={trailer['key']}"
        st.video(youtube_url)
    else:
        st.write("Trailer not available.")

    # 👨‍🎭 Cast
    st.subheader("🎭 Cast")
    cast = details.get("credits", {}).get("cast", [])[:10]
    cast_cols = st.columns(5)

    for index, actor in enumerate(cast):
        with cast_cols[index % 5]:
            if actor.get("profile_path"):
                st.image(IMAGE_BASE + actor["profile_path"])
            st.write(actor["name"])

    # 📺 Watch Providers
    st.subheader("📺 Available On")
    providers = get_watch_providers(movie_id)

    if providers and "flatrate" in providers:
        provider_cols = st.columns(5)
        for index, provider in enumerate(providers["flatrate"]):
            with provider_cols[index % 5]:
                logo = "https://image.tmdb.org/t/p/w200" + provider["logo_path"]
                st.image(logo)
                st.write(provider["provider_name"])

        if providers.get("link"):
            st.markdown(f"[🔴 Watch Now]({providers['link']})")
    else:
        st.info("Streaming availability may vary by country.")
