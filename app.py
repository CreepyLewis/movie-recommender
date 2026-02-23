import streamlit as st
import requests

# ===============================
# CONFIG
# ===============================

TMDB_API_KEY = st.secrets["TMDB_API_KEY"]  # Put your key in Streamlit Secrets
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_URL = "https://image.tmdb.org/t/p/w500"
LOGO_URL = "https://image.tmdb.org/t/p/w200"

st.set_page_config(page_title="Creepy-Movie Recommendation", layout="wide")

# ===============================
# DARK NETFLIX STYLE
# ===============================

st.markdown("""
<style>
body {
    background-color: #141414;
    color: white;
}
.movie-card {
    text-align: center;
}
.provider-logo {
    margin: 5px;
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 Creepy-Movie Recommendation")
st.write("Kenya’s Movie Discovery Engine 🇰🇪")

# ===============================
# SEARCH
# ===============================

query = st.text_input("Search for a movie")

def search_movies(query):
    url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query
    }
    response = requests.get(url, params=params)
    return response.json()

def get_watch_providers(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/watch/providers"
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params)
    data = response.json()
    return data.get("results", {}).get("KE", {})

# ===============================
# DISPLAY RESULTS
# ===============================

if query:
    data = search_movies(query)

    if data.get("results"):
        for movie in data["results"][:8]:

            col1, col2 = st.columns([1,2])

            with col1:
                if movie.get("poster_path"):
                    st.image(IMAGE_URL + movie["poster_path"])

            with col2:
                st.subheader(movie["title"])
                st.write(f"⭐ Rating: {movie['vote_average']}")
                st.write(f"📅 Release: {movie['release_date']}")
                st.write(movie["overview"])

                # ===============================
                # WATCH PROVIDERS (KENYA)
                # ===============================

                providers = get_watch_providers(movie["id"])

                if providers:

                    st.write("### 📺 Available in Kenya")

                    if "flatrate" in providers:
                        cols = st.columns(len(providers["flatrate"]))
                        for i, provider in enumerate(providers["flatrate"]):
                            with cols[i]:
                                st.image(
                                    LOGO_URL + provider["logo_path"],
                                    width=60
                                )

                                # Clickable Watch Link
                                link = providers.get("link")
                                if link:
                                    st.markdown(
                                        f"[▶ Watch Now]({link})",
                                        unsafe_allow_html=True
                                    )
                else:
                    st.write("❌ Not available for streaming in Kenya")

            st.markdown("---")

    else:
        st.warning("No movies found.")
