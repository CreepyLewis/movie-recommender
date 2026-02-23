import streamlit as st
import requests

# ===============================
# CONFIG
# ===============================
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]  # Use Streamlit secrets
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_URL = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="Creepy Movie Recommendation", layout="wide")

# ===============================
# DARK NETFLIX STYLE
# ===============================
st.markdown("""
<style>
body {
    background-color: #0e0e0e;
    color: white;
}
.stApp {
    background-color: #0e0e0e;
}
.movie-card img {
    border-radius: 10px;
    transition: 0.3s;
}
.movie-card img:hover {
    transform: scale(1.05);
}
h1, h2, h3, h4 {
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 Creepy Movie Recommendation")

# ===============================
# SEARCH FUNCTION
# ===============================
def search_movies(query):
    url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query
    }
    response = requests.get(url, params=params)
    return response.json().get("results", [])

# ===============================
# GET TRAILER
# ===============================
def get_trailer(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/videos"
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params)
    results = response.json().get("results", [])
    for video in results:
        if video["type"] == "Trailer" and video["site"] == "YouTube":
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None

# ===============================
# GET WATCH PROVIDERS
# ===============================
def get_watch_providers(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/watch/providers"
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params)
    data = response.json().get("results", {})
    
    # Kenya providers
    if "KE" in data:
        return data["KE"]
    return None

# ===============================
# SEARCH BAR
# ===============================
query = st.text_input("Search for a movie")

if query:
    movies = search_movies(query)

    if movies:
        cols = st.columns(5)

        for index, movie in enumerate(movies[:10]):
            with cols[index % 5]:
                if movie["poster_path"]:
                    poster_url = IMAGE_URL + movie["poster_path"]

                    if st.button("", key=movie["id"]):
                        st.session_state.selected_movie = movie

                    st.image(poster_url)

        # ===============================
        # MOVIE DETAILS POPUP
        # ===============================
        if "selected_movie" in st.session_state:
            movie = st.session_state.selected_movie

            st.divider()
            st.subheader(movie["title"])
            st.write(f"⭐ Rating: {movie['vote_average']}")
            st.write(f"📅 Release Date: {movie['release_date']}")
            st.write(movie["overview"])

            # Trailer
            trailer_url = get_trailer(movie["id"])
            if trailer_url:
                st.markdown(f"[▶ Watch Trailer]({trailer_url})")

            # Watch Providers
            providers = get_watch_providers(movie["id"])

            if providers:
                st.subheader("📺 Available in Kenya")

                # Streaming
                if "flatrate" in providers:
                    st.write("Streaming:")
                    cols = st.columns(len(providers["flatrate"]))

                    for i, provider in enumerate(providers["flatrate"]):
                        with cols[i]:
                            logo = "https://image.tmdb.org/t/p/w200" + provider["logo_path"]
                            st.image(logo)
                            if "link" in providers:
                                st.markdown(f"[Watch Now]({providers['link']})")

                # Rent
                if "rent" in providers:
                    st.write("Rent:")
                    cols = st.columns(len(providers["rent"]))

                    for i, provider in enumerate(providers["rent"]):
                        with cols[i]:
                            logo = "https://image.tmdb.org/t/p/w200" + provider["logo_path"]
                            st.image(logo)
                            if "link" in providers:
                                st.markdown(f"[Watch Now]({providers['link']})")

                # Buy
                if "buy" in providers:
                    st.write("Buy:")
                    cols = st.columns(len(providers["buy"]))

                    for i, provider in enumerate(providers["buy"]):
                        with cols[i]:
                            logo = "https://image.tmdb.org/t/p/w200" + provider["logo_path"]
                            st.image(logo)
                            if "link" in providers:
                                st.markdown(f"[Watch Now]({providers['link']})")

            else:
                st.write("❌ Not available in Kenya currently.")

    else:
        st.warning("No movies found.")
