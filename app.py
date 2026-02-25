import streamlit as st
import requests

# ===============================
# CONFIG
# ===============================
st.set_page_config(page_title="Creepy - Kenya Movie Discovery", layout="wide")

API_KEY = st.secrets["TMDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
BACKDROP_BASE = "https://image.tmdb.org/t/p/w1280"
LOGO_BASE = "https://image.tmdb.org/t/p/w200"

# ===============================
# DARK NETFLIX STYLE + RED BUTTONS
# ===============================
st.markdown("""
<style>
.stApp { background-color: #141414; color: white; }
h1,h2,h3,h4 { color: white; }
img { border-radius: 8px; transition: transform 0.3s ease; cursor: pointer; }
img:hover { transform: scale(1.08); }

/* Red Buttons */
.stButton>button {
    background-color: #E50914;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 0.25rem 0.75rem;
    font-weight: bold;
}
.stButton>button:hover {
    background-color: #B20710;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# SESSION STATE
# ===============================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

# ===============================
# SAFE REQUEST
# ===============================
def safe_request(url, params):
    try:
        r = requests.get(url, params=params)
        if r.status_code == 200:
            return r.json()
        return {}
    except:
        return {}

# ===============================
# API FUNCTIONS
# ===============================
def get_movies(endpoint):
    data = safe_request(f"{BASE_URL}{endpoint}", {"api_key": API_KEY})
    return data.get("results", [])

def search_movies(query):
    data = safe_request(
        f"{BASE_URL}/search/movie",
        {"api_key": API_KEY, "query": query}
    )
    return data.get("results", [])

def get_movie_full(movie_id):
    return safe_request(
        f"{BASE_URL}/movie/{movie_id}",
        {"api_key": API_KEY, "append_to_response": "credits,videos"}
    )

def get_watch_providers(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/watch/providers"
    params = {"api_key": API_KEY}

    data = safe_request(url, params)
    return data.get("results", {}).get("KE")

# ===============================
# WATCH PROVIDERS (KENYA)
# ===============================
providers = get_watch_providers(movie_id)

st.subheader("📺 Available in Kenya 🇰🇪")

if providers:

    # Direct link to TMDB provider page
    watch_link = providers.get("link")

    def display_provider_section(title, provider_list):
        if provider_list:
            st.markdown(f"#### {title}")
            cols = st.columns(len(provider_list))

            for i, provider in enumerate(provider_list):
                with cols[i]:
                    logo_path = provider.get("logo_path")
                    provider_name = provider.get("provider_name")

                    if logo_path:
                        st.image(LOGO_BASE + logo_path, width=80)

                    st.caption(provider_name)

                    if watch_link:
                        st.markdown(
                            f"""
                            <a href="{watch_link}" target="_blank">
                                <button style="
                                    background-color:#E50914;
                                    color:white;
                                    border:none;
                                    padding:6px 12px;
                                    border-radius:4px;
                                    cursor:pointer;">
                                    Watch Now
                                </button>
                            </a>
                            """,
                            unsafe_allow_html=True
                        )

    # Streaming (Subscription)
    display_provider_section("🎬 Streaming", providers.get("flatrate"))

    # Rent
    display_provider_section("💰 Rent", providers.get("rent"))

    # Buy
    display_provider_section("🛒 Buy", providers.get("buy"))

else:
    st.info("❌ This movie is currently not available on major streaming platforms in Kenya.")

# ===============================
# MOVIE PAGE
# ===============================
if st.session_state.page == "movie":

    movie_id = st.session_state.selected_movie
    movie = get_movie_full(movie_id)

    # Red Back Button
    if st.button("⬅ Back to Home"):
        st.session_state.page = "home"
        st.session_state.selected_movie = None
        st.rerun()

    if movie.get("backdrop_path"):
        st.image(BACKDROP_BASE + movie["backdrop_path"], use_container_width=True)

    st.title(movie.get("title"))

    col1, col2 = st.columns([1, 2])

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
        if v.get("type") == "Trailer" and v.get("site") == "YouTube":
            trailer = v.get("key")
            break

    if trailer:
        st.subheader("🎬 Trailer")
        st.video(f"https://www.youtube.com/watch?v={trailer}")

    # Cast with pictures
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
        for i, p in enumerate(providers["flatrate"]):
            with cols[i]:
                if p.get("logo_path"):
                    st.image(LOGO_BASE + p["logo_path"])
                if providers.get("link"):
                    st.markdown(f"[Watch Now]({providers['link']})")
    else:
        st.warning("Not available in Kenya.")

# ===============================
# HOME PAGE
# ===============================
else:

    st.title("🎬 Creepy - Kenya Movie Discovery")

    # Search bar
    query = st.text_input("🔍 Search for a movie")

    if query:
        results = search_movies(query)
        if results:
            st.subheader("Search Results")
            cols = st.columns(6)
            for i, movie in enumerate(results[:12]):
                with cols[i % 6]:
                    if movie.get("poster_path"):
                        st.image(IMAGE_BASE + movie["poster_path"])
                    # Red View Details button
                    if st.button("View Details", key=f"search_{movie['id']}"):
                        st.session_state.selected_movie = movie["id"]
                        st.session_state.page = "movie"
                        st.rerun()
        else:
            st.warning("No movies found.")

    else:

        def display_row(title, endpoint):
            st.subheader(title)
            movies = get_movies(endpoint)
            cols = st.columns(6)

            for i, movie in enumerate(movies[:18]):
                with cols[i % 6]:
                    if movie.get("poster_path"):
                        st.image(IMAGE_BASE + movie["poster_path"])
                    # Red View Details button
                    if st.button("View Details", key=f"{title}_{movie['id']}"):
                        st.session_state.selected_movie = movie["id"]
                        st.session_state.page = "movie"
                        st.rerun()

        display_row("🔥 Popular", "/movie/popular")
        display_row("💥 Action", "/discover/movie?with_genres=28")
        display_row("😂 Comedy", "/discover/movie?with_genres=35")
        display_row("👻 Horror", "/discover/movie?with_genres=27")
