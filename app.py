## import all requried libraries
import streamlit as st
import pickle
import pandas as pd
import requests






API_KEY = 'eb1f900105b692189941c84773666960'


# this function fetch movie poster using tmdb api
def fetch_poster(movie_id):

    # sending request to tmdb server
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
    )
    st.text(response)
    # converting response into json format
    data = response.json()

    # showing response status in streamlit
    st.text(response)

    # checking poster exist or not
    if data.get('poster_path'):

        # creating full image url
        return "https://image.tmdb.org/t/p/w500" + data['poster_path']

    else:
        # if poster not found then show dummy image
        return "https://via.placeholder.com/500x750?text=No+Image"


# main recommend function
# all ml and nlp model trainning work done in another jupyter notebook file
def recommend(movie):

    # finding selected movie from dataframe
    movie_list = movies[movies['title'] == movie]

    # if movie not found
    if movie_list.empty:
        st.error("Movie not found")
        return [], []

    # getting index of selected movie
    movie_index = movie_list.index[0]

    # getting similarity score of selected movie
    distance = similarity[movie_index]

    # sorting movies based on highest similarity
    # [1:6] because first movie is always same movie itself
    movie_list = sorted(
        list(enumerate(distance)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    # empty list for storing movie names
    recommended_movies = []

    # empty list for storing posters
    recommend_moive_posters = []

    # loop through recommended movies
    for i in movie_list:

        # getting movie id from dataframe
        movie_id = movies.iloc[i[0]].movie_id

        # appending movie title
        recommended_movies.append(
            movies.iloc[i[0]].title
        )

        # appending movie poster
        recommend_moive_posters.append(
            fetch_poster(movie_id)
        )

    # return both movie names and posters
    return recommended_movies, recommend_moive_posters


# loading movie dictionary file
movies_dic = pickle.load(open('movies_dict.pkl', 'rb'))

# converting dictionary into dataframe
movies = pd.DataFrame(movies_dic)

# loading similarity matrix file generated from ml model
similarity = pickle.load(open('similarity.pkl', 'rb'))


# streamlit app title
st.title('Movie Recommunder Systemmm')


# dropdown for selecting movie
selected_movie_name = st.selectbox(
    'search here',
    movies['title'].values
)


# when user click recommend button
if st.button('Recommend'):

    # calling recommend function
    name, poster = recommend(selected_movie_name)

    # creating 5 columns for showing movies
    col1, col2, col3, col4, col5 = st.columns(5)

    # movie 1
    with col1:
        st.header(name[0])
        st.image(poster[0])

    # movie 2
    with col2:
        st.header(name[1])
        st.image(poster[1])

    # movie 3
    with col3:
        st.header(name[2])
        st.image(poster[2])

    # movie 4
    with col4:
        st.header(name[3])
        st.image(poster[3])

    # movie 5
    with col5:
        st.header(name[4])
        st.image(poster[4])