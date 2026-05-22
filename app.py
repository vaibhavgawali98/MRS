# import all required libraries
import streamlit as st
import pickle
import pandas as pd
import requests
from sklearn.metrics.pairwise import cosine_similarity

API_KEY = 'eb1f900105b692189941c84773666960'

# loading vector file
vectors = pickle.load(open('vectorss.pkl', 'rb'))

# creating similarity matrix
similarity = cosine_similarity(vectors)

# loading movie dictionary
movies_dic = pickle.load(open('movies_dict.pkl', 'rb'))

# converting into dataframe
movies = pd.DataFrame(movies_dic)


# function to fetch movie poster
def fetch_poster(movie_id):

    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'

    response = requests.get(url)

    # convert response to json
    data = response.json()

    # check poster exists
    if data.get('poster_path'):

        poster_path = data['poster_path']

        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path

        return full_path

    else:
        return "https://via.placeholder.com/500x750?text=No+Image"


# recommendation function
def recommend(movie):

    movie_list = movies[movies['title'] == movie]

    if movie_list.empty:
        st.error("Movie not found")
        return [], []

    movie_index = movie_list.index[0]

    distances = similarity[movie_index]

    recommended_movies = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    movie_names = []
    movie_posters = []

    for i in recommended_movies:

        movie_id = movies.iloc[i[0]].movie_id

        movie_names.append(
            movies.iloc[i[0]].title
        )

        movie_posters.append(
            fetch_poster(movie_id)
        )

    return movie_names, movie_posters


# streamlit title
st.title('Movie Recommender System')

# movie dropdown
selected_movie_name = st.selectbox(
    'Search Movie',
    movies['title'].values
)

# recommend button
if st.button('Recommend'):

    names, posters = recommend(selected_movie_name)

    if len(names) >= 5:

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.text(names[0])
            st.image(posters[0])

        with col2:
            st.text(names[1])
            st.image(posters[1])

        with col3:
            st.text(names[2])
            st.image(posters[2])

        with col4:
            st.text(names[3])
            st.image(posters[3])

        with col5:
            st.text(names[4])
            st.image(posters[4])
