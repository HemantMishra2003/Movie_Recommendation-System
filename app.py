import streamlit as st
import pickle
import pandas as pd
import httpx


# index.html ko read karo
with open("index.html", "r", encoding="utf-8") as f:
    html_data = f.read()

# Streamlit me show karo
st.components.v1.html(html_data, height=600, scrolling=True)
# Load data
mov = pickle.load(open("movies_overview.pkl", "rb"))
m = pd.DataFrame(mov)

movies_dict = pickle.load(open("movies_list.pkl", "rb"))
movies = pd.DataFrame(movies_dict)

try:
    similarity = pickle.load(open("similarity (1).pkl", "rb"))
except:
    similarity = None

st.title("Movie Recommendation System")

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=353e5fee8ad23a873c3205bf9174b018&language=en-US"
    try:
        with httpx.Client(verify=False) as client:
            response = client.get(url)
            data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/original" + poster_path
        else:
            return None
    except:
        return None

def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].id
        recommended_movies.append(movies.iloc[i[0]].title)
        poster = fetch_poster(movie_id)
        recommended_movies_posters.append(poster)

    return recommended_movies, recommended_movies_posters

# ========================
# Slideable Trending Movies Carousel using HTML + CSS
# ========================
st.header(":red[Trending / Popular Movies]")
carousel_ids = [1632, 299536, 17455, 2830, 429422, 9722, 13972, 240]

html_code = '<div style="display:flex; overflow-x:auto; gap:10px;">'
for movie_id in carousel_ids:
    poster = fetch_poster(movie_id)
    if poster:
        html_code += f'<img src="{poster}" style="height:200px; border-radius:10px;">'
html_code += '</div>'

st.components.v1.html(html_code, height=220)

# ========================
# Movie selection
# ========================
selected_movie_name = st.selectbox(':red[Movies similar to]', movies["title"].values)
movie_index = movies["title"].to_list().index(selected_movie_name)

st.header(':red[Movie Name]')
st.markdown(f'{selected_movie_name}')

st.header(':red[Genre]')
st.markdown(f'{m["genre"][movie_index]}')

st.header(':red[Overview]')
st.markdown(f'{m["overview"][movie_index]}')

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(2)
    for col, name, poster in zip(cols, names, posters):
        col.text(name)
        if poster:
            col.image(poster)