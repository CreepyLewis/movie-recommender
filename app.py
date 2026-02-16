import streamlit as st

# -----------------------------
# Sample movie dataset (expandable / replace with TMDB API)
# Each movie has: title, poster URL, recommended movies with posters
# -----------------------------
movies = {
    "Avatar": {
        "poster": "https://upload.wikimedia.org/wikipedia/en/b/b0/Avatar-Teaser-Poster.jpg",
        "recommendations": [
            {"title": "Titanic", "poster": "https://upload.wikimedia.org/wikipedia/en/2/2e/Titanic_poster.jpg"},
            {"title": "Avengers", "poster": "https://upload.wikimedia.org/wikipedia/en/f/f9/Avengers_Infinity_War_poster.jpg"},
            {"title": "Guardians of the Galaxy", "poster": "https://upload.wikimedia.org/wikipedia/en/8/8f/GotG_Vol_2_poster.jpg"}
        ]
    },
    "Titanic": {
        "poster": "https://upload.wikimedia.org/wikipedia/en/2/2e/Titanic_poster.jpg",
        "recommendations": [
            {"title": "Avatar", "poster": "https://upload.wikimedia.org/wikipedia/en/b/b0/Avatar-Teaser-Poster.jpg"},
            {"title": "The Notebook", "poster": "https://upload.wikimedia.org/wikipedia/en/8/86/The_Notebook_poster.jpg"},
            {"title": "Romeo + Juliet", "poster": "https://upload.wikimedia.org/wikipedia/en/d/d0/Romeo_and_juliet_ver2.jpg"}
        ]
    },
    "Inception": {
        "poster": "https://upload.wikimedia.org/wikipedia/en/7/7f/Inception_ver3.jpg",
        "recommendations": [
            {"title": "Interstellar", "poster": "https://upload.wikimedia.org/wikipedia/en/b/bc/Interstellar_film_poster.jpg"},
            {"title": "The Matrix", "poster": "https://upload.wikimedia.org/wikipedia/en/c/c1/The_Matrix_Poster.jpg"},
            {"title": "Shutter Island", "poster": "https://upload.wikimedia.org/wikipedia/en/7/76/Shutterislandposter.jpg"}
        ]
    }
}

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")
st.title("🎬 Movie Recommender")

# Dropdown for movie selection
movie_name = st.selectbox("Select a movie:", list(movies.keys()))

# Display main movie poster
st.subheader(f"🎥 {movie_name}")
st.image(movies[movie_name]["poster"], width=250)

st.write("---")
st.subheader("You might also like:")

# Netflix-style grid layout for recommendations
recommendations = movies[movie_name]["recommendations"]
cols = st.columns(len(recommendations))

for idx, rec in enumerate(recommendations):
    with cols[idx]:
        st.image(rec["poster"], width=150)
        st.caption(rec["title"])

# -----------------------------
# Notes for scaling:
# -----------------------------
# 1. You can expand the `movies` dictionary to 100+ movies.
# 2. Replace static poster URLs with TMDB API calls for dynamic posters.
# 3. Use st.columns to create a grid layout like Netflix.
