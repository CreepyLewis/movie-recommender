import streamlit as st
import requests

# ==================================
# CONFIG
# ==================================
st.set_page_config(page_title="Creepy - Kenya Movie Discovery", layout="wide")

API_KEY = st.secrets["TMDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
BACKDROP_BASE = "https://image.tmdb.org/t/p/w1280"
LOGO_BASE = "https://image.tmdb.org/t/p/w200"

# ==================================
# NETFLIX DARK STYLE + HOVER
# ==================================
st.markdown("""
<style>
.stApp { background-color: #141414; color: white; }

.poster-container {
    position: relative;
    cursor: pointer;
}

.poster-container img {
    border-radius: 8px;
    transition: transform 0.3s ease;
}

.poster-container:hover img {
    transform: scale(1.05);
}

.overlay {
    position: absolute;
    bottom: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.9), transparent);
    width: 100%;
    padding: 10px;
    border-radius: 8px;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.poster-container:hover .overlay {
    opacity: 1;
}

.overlay-text {
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# ==================================
# SESSION STATE
# ==================================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

if "page_counters" not in st.session_state:
    st.session_state.page_counters = {}

# ==================================
# API SAFE REQUEST
# ==================================
def safe_request(url, params):
    try:
        r = requests.get(url, params=params)
        if r.status_code == 200:
            return r.json()
        return {}
    except:
        return {}

# ==================================
# API FUNCTIONS
# ==================================
def get_movies(endpoint, page=1):
    data = safe_request(
        f"{BASE_URL}{endpoint}",
        {"api_key": API_KEY, "page": page}
    )
    return data.get("results", [])

def get_movie_full(movie_id):
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

def get_ai_recommendations(movie_id):
    data = safe_request(
        f"{BASE_URL}/movie/{movie_id}/similar",
        {"api_key": API_KEY}
    )
    return data.get("results", [])[:12]

# ==================================
# CLICKABLE POSTER
# ==================================
def clickable_poster(movie):
    year = movie.get("release_date", "")[:4]
    rating = movie.get("vote_average")

    poster_html = f"""
    <div class="poster-container">
        <img src="{IMAGE_BASE + movie['poster_path']}" width="100%">
        <div class="overlay">
            <div class="overlay-text">
                ⭐ {rating} | {year}
            </div>
        </div>
    </div>
    """

    if st.button(" ", key=f"poster_{movie['id']}"):
        st.session_state.selected_movie = movie["id"]
        st.session_state.page = "movie"
        st.rerun()

    st.markdown(poster_html, unsafe_allow_html=True)

# ==================================
# MOVIE PAGE
# ==================================
if st.session_state.page == "movie":

    movie_id = st.session_state.selected_movie
    movie = get_movie_full(movie_id)

    if st.button("⬅ Back"):
        st.session_state.page = "home"
        st.rerun()

    if movie.get("backdrop_path"):
        st.image(BACKDROP_BASE + movie["backdrop_path"], use_container_width=True)

    st.title(movie.get("title"))
    st.write(movie.get("overview"))

    # Cast
    cast = movie.get("credits", {}).get("cast", [])[:6]
    st.subheader("🎭 Cast")
    cols = st.columns(len(cast))
    for i, actor in enumerate(cast):
        with cols[i]:
            if actor.get("profile_path"):
                st.image(IMAGE_BASE + actor["profile_path"])
            st.caption(actor.get("name"))

    # Trailer
    videos = movie.get("videos", {}).get("results", [])
    for v in videos:
        if v.get("type") == "Trailer" and v.get("site") == "YouTube":
            st.subheader("🎬 Trailer")
            st.video(f"https://youtube.com/watch?v={v['key']}")
            break

    # Watch Providers
    providers = get_watch_providers(movie_id)
    st.subheader("📺 Watch in Kenya 🇰🇪")
    if providers and "flatrate" in providers:
        cols = st.columns(len(providers["flatrate"]))
        for i, p in enumerate(providers["flatrate"]):
            with cols[i]:
                st.image(LOGO_BASE + p["logo_path"])
                if providers.get("link"):
                    st.markdown(f"[Watch Now]({providers['link']})")
    else:
        st.warning("Not available in Kenya")

    # AI Recommendations
    st.subheader("🤖 You May Also Like")
    recommendations = get_ai_recommendations(movie_id)
    cols = st.columns(6)
    for i, rec in enumerate(recommendations):
        if rec.get("poster_path"):
            with cols[i % 6]:
                clickable_poster(rec)

# ==================================
# HOME PAGE
# ==================================
else:

    st.title("🎬 Creepy - Kenya Movie Discovery")

    def display_row(title, endpoint):
        st.subheader(title)

        if title not in st.session_state.page_counters:
            st.session_state.page_counters[title] = 1

        page = st.session_state.page_counters[title]
        movies = get_movies(endpoint, page)

        cols = st.columns(6)
        for i, movie in enumerate(movies):
            if movie.get("poster_path"):
                with cols[i % 6]:
                    clickable_poster(movie)

        if st.button(f"Load More {title}", key=f"load_{title}"):
            st.session_state.page_counters[title] += 1
            st.rerun()

    display_row("🔥 Trending in Kenya", "/trending/movie/week")
    display_row("🎬 Popular", "/movie/popular")
    display_row("💥 Action", "/discover/movie?with_genres=28")
    display_row("😂 Comedy", "/discover/movie?with_genres=35")
    display_row("👻 Horror", "/discover/movie?with_genres=27")
