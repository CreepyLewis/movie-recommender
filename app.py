import streamlit as st
import requests

# ==============================
# CONFIG
# ==============================
st.set_page_config(layout="wide")

API_KEY = "YOUR_TMDB_API_KEY"

# ==============================
# CSS (DESKTOP + MOBILE)
# ==============================
st.markdown("""
<style>

/* Global */
body {
    background-color: #0d0d0d;
    color: white;
}

/* Movie poster hover (Desktop only) */
@media (min-width: 769px) {
    .movie-poster:hover {
        transform: scale(1.07);
        transition: 0.3s ease-in-out;
        cursor: pointer;
    }
}

/* Mobile Optimization */
@media (max-width: 768px) {
    .actor-scroll {
        display: flex;
        overflow-x: auto;
        gap: 15px;
        padding-bottom: 10px;
        scroll-snap-type: x mandatory;
    }
    .actor-card {
        min-width: 120px;
        text-align: center;
        scroll-snap-align: start;
    }
    .actor-scroll::-webkit-scrollbar {
        display: none;
    }
}

/* Red Buttons */
.stButton>button {
    background-color: #e50914;
    color: white;
    border-radius: 6px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# TMDB FUNCTIONS
# ==============================
def safe_get(url, params):
    response = requests.get(url, params=params)
    data = response.json()
    return data if isinstance(data, dict) else {}

def get_popular_movies():
    url = "https://api.themoviedb.org/3/movie/popular"
    params = {"api_key": API_KEY}
    data = safe_get(url, params)
    return data.get("results", [])

def search_movies(query):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": API_KEY, "query": query}
    data = safe_get(url, params)
    return data.get("results", [])

def get_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": API_KEY}
    return safe_get(url, params)

def get_movie_credits(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
    params = {"api_key": API_KEY}
    data = safe_get(url, params)
    return data.get("cast", [])

def get_movie_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos"
    params = {"api_key": API_KEY}
    data = safe_get(url, params)
    for video in data.get("results", []):
        if video["type"] == "Trailer" and video["site"] == "YouTube":
            return f"https://www.youtube.com/embed/{video['key']}"
    return None

def get_watch_providers(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers"
    params = {"api_key": API_KEY}
    data = safe_get(url, params)
    return data.get("results", {}).get("KE", {})

# ==============================
# SESSION STATE
# ==============================
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

# ==============================
# HOME PAGE
# ==============================
if st.session_state.selected_movie is None:

    st.title("🎬 Creepy Movie Recommendation")

    search_query = st.text_input("Search for a movie")

    if search_query:
        movies = search_movies(search_query)
    else:
        movies = get_popular_movies()

    cols = st.columns(5)

    for index, movie in enumerate(movies):
        with cols[index % 5]:
            poster_path = movie.get("poster_path")
            if poster_path:
                poster = f"https://image.tmdb.org/t/p/w500{poster_path}"
                st.markdown(
                    f"""
                    <img src="{poster}" width="100%" class="movie-poster">
                    """,
                    unsafe_allow_html=True
                )

            if st.button("View Details", key=movie["id"]):
                st.session_state.selected_movie = movie["id"]
                st.rerun()

# ==============================
# MOVIE DETAILS PAGE
# ==============================
else:
    movie_id = st.session_state.selected_movie
    details = get_movie_details(movie_id)
    cast = get_movie_credits(movie_id)
    trailer = get_movie_trailer(movie_id)
    providers = get_watch_providers(movie_id)

    if st.button("⬅ Back Home"):
        st.session_state.selected_movie = None
        st.rerun()

    col1, col2 = st.columns([1, 2])

    with col1:
        if details.get("poster_path"):
            poster = f"https://image.tmdb.org/t/p/w500{details['poster_path']}"
            st.image(poster)

    with col2:
        st.title(details.get("title", "No Title"))
        st.write(details.get("overview", "No description available."))
        st.write("⭐ Rating:", details.get("vote_average", "N/A"))
        st.write("📅 Release Date:", details.get("release_date", "N/A"))

    # Trailer
    if trailer:
        st.markdown("## 🎥 Trailer")
        st.markdown(
            f"""
            <iframe width="100%" height="400"
            src="{trailer}"
            frameborder="0"
            allowfullscreen></iframe>
            """,
            unsafe_allow_html=True
        )

    # Cast
    st.markdown("## 🎭 Cast")

    st.markdown('<div class="actor-scroll">', unsafe_allow_html=True)

    for actor in cast[:10]:
        if actor.get("profile_path"):
            actor_img = f"https://image.tmdb.org/t/p/w200{actor['profile_path']}"
            st.markdown(
                f"""
                <div class="actor-card">
                    <img src="{actor_img}" width="100">
                    <p style="color:white;font-size:14px;">{actor['name']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown('</div>', unsafe_allow_html=True)

    # Watch Providers
    st.markdown("## 📺 Available On")

    if providers:
        link = providers.get("link")

        for category in ["flatrate", "free", "ads"]:
            if category in providers:
                for provider in providers[category]:
                    logo = f"https://image.tmdb.org/t/p/w200{provider['logo_path']}"
                    st.markdown(
                        f"""
                        <a href="{link}" target="_blank">
                            <img src="{logo}" width="80">
                        </a>
                        """,
                        unsafe_allow_html=True
                    )
    else:
        st.info("Streaming availability data not available for Kenya.")
