import streamlit as st
import requests

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="Creepy - Kenya Movie Discovery", layout="wide")

API_KEY = st.secrets["TMDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
BACKDROP_BASE = "https://image.tmdb.org/t/p/w1280"
LOGO_BASE = "https://image.tmdb.org/t/p/w200"

# =============================
# DARK NETFLIX STYLE + HOVER
# =============================
st.markdown("""
<style>
.stApp { background-color: #141414; color: white; }
h1,h2,h3,h4 { color: white; }

.poster-container {
    position: relative;
    display: inline-block;
    margin-bottom: 10px;
}
.poster-img {
    border-radius: 6px;
    transition: transform 0.3s ease;
    width: 100%;
}
.poster-container:hover .poster-img {
    transform: scale(1.08);
}
.overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: rgba(0,0,0,0.7);
    color: white;
    opacity: 0;
    transition: opacity 0.3s;
    padding: 5px;
    border-radius: 0 0 6px 6px;
    font-size: 14px;
}
.poster-container:hover .overlay {
    opacity: 1;
}
</style>
""", unsafe_allow_html=True)

# =============================
# SESSION STATE
# =============================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None
if "row_limits" not in st.session_state:
    st.session_state.row_limits = {}  # track movies per row

# =============================
# SAFE REQUEST
# =============================
def safe_request(url, params):
    try:
        r = requests.get(url, params=params)
        if r.status_code == 200:
            return r.json()
        return {}
    except:
        return {}

# =============================
# API FUNCTIONS
# =============================
def get_movies(endpoint):
    data = safe_request(f"{BASE_URL}{endpoint}", {"api_key": API_KEY})
    return data.get("results", [])

def search_movies(query):
    data = safe_request(f"{BASE_URL}/search/movie", {"api_key": API_KEY, "query": query})
    return data.get("results", [])

def get_movie_full(movie_id):
    return safe_request(f"{BASE_URL}/movie/{movie_id}", {"api_key": API_KEY, "append_to_response": "credits,videos"})

def get_watch_providers(movie_id):
    data = safe_request(f"{BASE_URL}/movie/{movie_id}/watch/providers", {"api_key": API_KEY})
    return data.get("results", {}).get("KE")

# =============================
# HELPER TO DISPLAY POSTER ROW
# =============================
def display_row(title, endpoint, row_key, load_more_step=6):
    st.subheader(title)
    movies = get_movies(endpoint)

    # Initialize row limit
    if row_key not in st.session_state.row_limits:
        st.session_state.row_limits[row_key] = min(load_more_step, len(movies))

    display_count = st.session_state.row_limits[row_key]
    cols = st.columns(6)

    for i, movie in enumerate(movies[:display_count]):
        with cols[i % 6]:
            poster = movie.get("poster_path")
            if poster:
                st.markdown(
                    f"""
                    <div class="poster-container" onclick="window.parent.streamlit.setComponentValue('{movie['id']}')">
                        <img src="{IMAGE_BASE+poster}" class="poster-img"/>
                        <div class="overlay">{movie.get('title')} ⭐ {movie.get('vote_average')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    # Load More button
    if display_count < len(movies):
        if st.button(f"Load More {title}", key=f"loadmore_{row_key}"):
            st.session_state.row_limits[row_key] += load_more_step
            st.experimental_rerun()

# =============================
# MOVIE PAGE
# =============================
if st.session_state.page == "movie":
    movie_id = st.session_state.selected_movie
    movie = get_movie_full(movie_id)

    if st.button("⬅ Back to Home"):
        st.session_state.page = "home"
        st.session_state.selected_movie = None
        st.rerun()

    if movie.get("backdrop_path"):
        st.image(BACKDROP_BASE + movie["backdrop_path"], use_container_width=True)

    st.title(movie.get("title"))
    col1, col2 = st.columns([1,2])

    with col1:
        if movie.get("poster_path"):
            st.image(IMAGE_BASE + movie["poster_path"])
    with col2:
        st.write(movie.get("overview"))
        st.write(f"⭐ Rating: {movie.get('vote_average')}")
        st.write(f"📅 Release: {movie.get('release_date')}")
        st.write(f"⏱ Runtime: {movie.get('runtime')} mins")

    # Trailer
    videos = movie.get("videos", {}).get("results", [])
    trailer = None
    for v in videos:
        if v.get("type")=="Trailer" and v.get("site")=="YouTube":
            trailer = v.get("key")
            break
    if trailer:
        st.subheader("🎬 Trailer")
        st.video(f"https://www.youtube.com/watch?v={trailer}")

    # Cast
    cast = movie.get("credits", {}).get("cast", [])[:8]
    if cast:
        st.subheader("🎭 Cast")
        cols = st.columns(len(cast))
        for i, actor in enumerate(cast):
            with cols[i]:
                if actor.get("profile_path"):
                    st.image(IMAGE_BASE + actor["profile_path"])
                st.caption(actor.get("name"))

    # Watch Providers
    providers = get_watch_providers(movie_id)
    st.subheader("📺 Available in Kenya 🇰🇪")
    if providers and "flatrate" in providers:
        cols = st.columns(len(providers["flatrate"]))
        for i,p in enumerate(providers["flatrate"]):
            with cols[i]:
                if p.get("logo_path"):
                    st.image(LOGO_BASE+p["logo_path"])
                if providers.get("link"):
                    st.markdown(f"[Watch Now]({providers['link']})")
    else:
        st.warning("Not available in Kenya.")

# =============================
# HOME PAGE
# =============================
else:
    st.title("🎬 Creepy - Kenya Movie Discovery")

    # Search Bar
    query = st.text_input("🔍 Search for a movie")
    if query:
        results = search_movies(query)
        if results:
            st.subheader("Search Results")
            cols = st.columns(6)
            for i,movie in enumerate(results[:12]):
                with cols[i%6]:
                    poster = movie.get("poster_path")
                    if poster:
                        st.markdown(
                            f"""
                            <div class="poster-container" onclick="window.parent.streamlit.setComponentValue('{movie['id']}')">
                                <img src="{IMAGE_BASE+poster}" class="poster-img"/>
                                <div class="overlay">{movie.get('title')} ⭐ {movie.get('vote_average')}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        # Streamlit can't handle JS onclick natively → We'll fix below

    else:
        # Genre Rows
        display_row("🔥 Popular", "/movie/popular", "popular")
        display_row("💥 Action", "/discover/movie?with_genres=28", "action")
        display_row("😂 Comedy", "/discover/movie?with_genres=35", "comedy")
        display_row("👻 Horror", "/discover/movie?with_genres=27", "horror")
