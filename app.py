import streamlit as st
import requests
import datetime

# =========================
# CONFIG
# =========================
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_URL = "https://image.tmdb.org/t/p/w500"
LOGO_URL = "https://image.tmdb.org/t/p/w200"

st.set_page_config(page_title="Creepy Movie Recommendation", layout="wide")

# =========================
# PWA SUPPORT
# =========================
st.markdown("""
<link rel="manifest" href="data:application/json,{
"name":"Creepy Movie Recommendation",
"short_name":"Creepy",
"display":"standalone",
"start_url":"/",
"background_color":"#0e0e0e",
"theme_color":"#e50914"
}">
<meta name="theme-color" content="#e50914">
""", unsafe_allow_html=True)

# =========================
# NETFLIX DARK UI
# =========================
st.markdown("""
<style>
.stApp { background-color:#0e0e0e; color:white; }
h1,h2,h3,h4,h5,h6,p,span,label { color:white !important; }
img { border-radius:10px; transition:transform 0.3s; }
img:hover { transform:scale(1.05); }
div.stButton > button {
    background-color:#e50914;
    color:white;
    border:none;
    border-radius:6px;
}
div.stButton > button:hover { background-color:#b20710; }
</style>
""", unsafe_allow_html=True)

st.title("🎬 Creepy Movie Recommendation")

# =========================
# SAFE REQUEST
# =========================
def safe_request(url, params):
    try:
        res = requests.get(url, params=params)
        return res.json()
    except:
        return {}

# =========================
# TMDB FUNCTIONS
# =========================
def get_movies(endpoint):
    return safe_request(f"{BASE_URL}{endpoint}",
                        {"api_key": TMDB_API_KEY}).get("results", [])

def search_movies(query):
    return safe_request(f"{BASE_URL}/search/movie",
                        {"api_key": TMDB_API_KEY, "query": query}).get("results", [])

def get_movie_details(movie_id):
    return safe_request(f"{BASE_URL}/movie/{movie_id}",
                        {"api_key": TMDB_API_KEY})

def get_trailer(movie_id):
    data = safe_request(f"{BASE_URL}/movie/{movie_id}/videos",
                        {"api_key": TMDB_API_KEY})
    for vid in data.get("results", []):
        if vid.get("type") == "Trailer" and vid.get("site") == "YouTube":
            return f"https://www.youtube.com/embed/{vid['key']}?autoplay=1"
    return None

def get_actors(movie_id):
    return safe_request(f"{BASE_URL}/movie/{movie_id}/credits",
                        {"api_key": TMDB_API_KEY}).get("cast", [])[:6]

def get_watch_providers(movie_id):
    return safe_request(f"{BASE_URL}/movie/{movie_id}/watch/providers",
                        {"api_key": TMDB_API_KEY}).get("results", {}).get("KE", {})

# =========================
# DISPLAY ROW
# =========================
def display_row(title, movies):
    st.subheader(title)
    cols = st.columns(6)
    for i, movie in enumerate(movies[:12]):
        poster = movie.get("poster_path")
        if poster:
            with cols[i % 6]:
                st.image(IMAGE_URL + poster)
                key = f"{title}_{movie['id']}"
                if st.button("View Details", key=key):
                    st.session_state.selected_id = movie["id"]
                    st.rerun()

# =========================
# ADMIN DASHBOARD
# =========================
def admin_dashboard():
    st.header("📊 Admin Dashboard")

    popular = get_movies("/movie/popular")
    now_playing = get_movies("/movie/now_playing")

    st.metric("Popular Movies Loaded", len(popular))
    st.metric("Now Playing (Cinema)", len(now_playing))
    st.metric("Current Date", datetime.date.today())

# =========================
# MAIN PAGE
# =========================
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

if st.sidebar.checkbox("Admin Login"):
    password = st.sidebar.text_input("Enter Password", type="password")
    if password == ADMIN_PASSWORD:
        st.session_state.admin_mode = True

if st.session_state.admin_mode:
    admin_dashboard()

elif "selected_id" not in st.session_state:

    query = st.text_input("Search movies...")

    if query:
        results = search_movies(query)
        if results:
            display_row("Search Results", results)
        else:
            st.warning("No movies found.")
    else:
        display_row("🔥 Popular Now", get_movies("/movie/popular"))
        display_row("💥 Action", get_movies("/discover/movie?with_genres=28"))
        display_row("😂 Comedy", get_movies("/discover/movie?with_genres=35"))
        display_row("👻 Horror", get_movies("/discover/movie?with_genres=27"))
        display_row("❤️ Romance", get_movies("/discover/movie?with_genres=10749"))

        # 🎬 Cinema Section
        st.divider()
        st.subheader("🎟 Now Showing in Kenya Cinemas")
        now_playing = get_movies("/movie/now_playing")
        display_row("In Cinemas", now_playing)

# =========================
# MOVIE DETAILS PAGE
# =========================
else:
    movie_id = st.session_state.selected_id
    movie = get_movie_details(movie_id)

    st.button("⬅ Back Home",
              on_click=lambda: st.session_state.pop("selected_id"))

    st.divider()

    col1, col2 = st.columns([1,2])

    with col1:
        if movie.get("poster_path"):
            st.image(IMAGE_URL + movie["poster_path"])

    with col2:
        st.header(movie.get("title"))
        st.write(f"⭐ {movie.get('vote_average')}")
        st.write(f"📅 {movie.get('release_date')}")
        st.write(movie.get("overview"))

    # ▶ Auto Play Trailer
    trailer = get_trailer(movie_id)
    if trailer:
        st.subheader("▶ Trailer")
        st.markdown(
            f'<iframe width="100%" height="400" src="{trailer}" frameborder="0" allowfullscreen></iframe>',
            unsafe_allow_html=True
        )

    # 🎭 Actors
    cast = get_actors(movie_id)
    if cast:
        st.subheader("🎭 Top Cast")
        cols = st.columns(len(cast))
        for i, actor in enumerate(cast):
            with cols[i]:
                if actor.get("profile_path"):
                    st.image(IMAGE_URL + actor["profile_path"])
                st.caption(actor.get("name"))

    # 📺 Watch Providers
    providers = get_watch_providers(movie_id)
    st.subheader("📺 Available in Kenya")

    if providers:
        for category in ["flatrate","rent","buy"]:
            if providers.get(category):
                st.write(category.capitalize())
                cols = st.columns(len(providers[category]))
                for i, p in enumerate(providers[category]):
                    with cols[i]:
                        if p.get("logo_path"):
                            st.image(LOGO_URL + p["logo_path"])
                if providers.get("link"):
                    st.markdown(f"[Watch Now]({providers['link']})")
    else:
        st.warning("Not available in Kenya.")
