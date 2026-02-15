import streamlit as st

# Simple movie dataset
movies = {
    "Avatar": ["Titanic", "Avengers", "Guardians of the Galaxy"],
    "Titanic": ["Avatar", "The Notebook", "Romeo + Juliet"],
    "Avengers": ["Iron Man", "Thor", "Captain America"],
    "Inception": ["Interstellar", "The Matrix", "Shutter Island"]
}

st.title("🎬 Movie Recommender")

movie_name = st.text_input("Enter a movie name:")

if movie_name:
    if movie_name in movies:
        st.write("You might also like:")
        for m in movies[movie_name]:
            st.write("👉", m)
    else:
        st.write("Sorry, movie not found in database.")