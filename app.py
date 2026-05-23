# import all required libraries
import streamlit as st
import pickle
import pandas as pd
import requests
from sklearn.metrics.pairwise import cosine_similarity

# =========================
# PAGE CONFIGURATION
# =========================

st.set_page_config(
    page_title="Netflix Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# =========================
# CUSTOM CSS (NETFLIX UI)
# =========================

st.markdown("""
<style>

/* main background */
.main {
    background-color: #141414;
    color: white;
}

/* remove default padding */
.block-container {
    padding-top: 1rem;
}

/* title styling */
.main-title {
    font-size: 50px;
    font-weight: bold;
    color: #E50914;
    text-align: center;
    margin-bottom: 20px;
}

/* movie card */
.movie-card {
    background-color: #1f1f1f;
    padding: 10px;
    border-radius: 12px;
    text-align: center;
    transition: 0.3s;
    margin-bottom: 20px;
}

/* hover effect */
.movie-card:hover {
    transform: scale(1.03);
    box-shadow: 0px 0px 15px rgba(229, 9, 20, 0.6);
}

/* button styling */
.stButton > button {
    background-color: #E50914;
    color: white;
    border-radius: 8px;
    border: none;
    width: 100%;
    height: 3em;
    font-size: 18px;
    font-weight: bold;
}

/* dropdown styling */
div[data-baseweb="select"] > div {
    background-color: #1f1f1f !important;
    color: white !important;
}

/* sidebar */
section[data-testid="stSidebar"] {
    background-color: #0d0d0d;
}

/* image hover */
img {
    border-radius: 10px;
    transition: 0.3s;
}

img:hover {
    transform: scale(1.03);
}

</style>
""", unsafe_allow_html=True)

# =========================
# API KEY
# =========================

API_KEY = 'eb1f900105b692189941c84773666960'

# =========================
# LOAD VECTOR FILE
# =========================

vectors = pickle.load(open('vectorss.pkl', 'rb'))

# create similarity matrix
similarity = cosine_similarity(vectors)

# =========================
# LOAD MOVIE DICTIONARY
# =========================

movies_dic = pickle.load(open('movies_dict.pkl', 'rb'))

# convert into dataframe
movies = pd.DataFrame(movies_dic)

# =========================
# FETCH MOVIE POSTER
# =========================

def fetch_poster(movie_id):

    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'

    response = requests.get(url)

    data = response.json()

    # if poster exists
    if data.get('poster_path'):

        poster_path = data['poster_path']

        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path

        return full_path

    # fallback image
    else:
        return "https://via.placeholder.com/500x750?text=No+Image"

# =========================
# FETCH MOVIE TRAILER
# =========================

def fetch_trailer(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"

    response = requests.get(url)

    data = response.json()

    # find trailer
    if data.get('results'):

        for video in data['results']:

            if video['type'] == 'Trailer':

                trailer_url = f"https://www.youtube.com/watch?v={video['key']}"

                return trailer_url

    return None

# =========================
# RECOMMENDATION FUNCTION
# =========================

def recommend(movie):

    movie_list = movies[movies['title'] == movie]

    if movie_list.empty:
        st.error("Movie not found")
        return [], [], []

    movie_index = movie_list.index[0]

    distances = similarity[movie_index]

    recommended_movies = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    movie_names = []
    movie_posters = []
    movie_trailers = []

    for i in recommended_movies:

        movie_id = movies.iloc[i[0]].movie_id

        # append movie title
        movie_names.append(
            movies.iloc[i[0]].title
        )

        # append poster
        movie_posters.append(
            fetch_poster(movie_id)
        )

        # append trailer
        movie_trailers.append(
            fetch_trailer(movie_id)
        )

    return movie_names, movie_posters, movie_trailers

# =========================
# SIDEBAR
# =========================

with st.sidebar:

    st.title("🎬 Movie AI")

    st.markdown("---")

    st.write("Netflix Style Movie Recommendation System")

    st.markdown("---")

    st.write("Built with:")
    st.write("✔ Streamlit")
    st.write("✔ Machine Learning")
    st.write("✔ TMDB API")

# =========================
# HERO SECTION
# =========================

st.markdown(
    "<div class='main-title'>🎬 NETFLIX MOVIE RECOMMENDER</div>",
    unsafe_allow_html=True
)

# optional banner image
st.image(
    "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba",
    use_container_width=True
)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# MOVIE SEARCH
# =========================

selected_movie_name = st.selectbox(
    '🔍 Search Movie',
    sorted(movies['title'].values)
)

# =========================
# RECOMMEND BUTTON
# =========================

if st.button('🎥 Recommend Movies'):

    # loading animation
    with st.spinner("Finding best movies for you..."):

        names, posters, trailers = recommend(selected_movie_name)

    # display recommendations
    if len(names) >= 5:

        cols = st.columns(5)

        for idx in range(5):

            with cols[idx]:

                # movie card start
                st.markdown(
                    "<div class='movie-card'>",
                    unsafe_allow_html=True
                )

                # movie poster
                st.image(posters[idx])

                # movie name
                st.markdown(
                    f"### {names[idx]}"
                )

                # fake netflix match percentage
                st.write(f"🔥 {90 - idx}% Match")

                # trailer button
                if trailers[idx]:

                    st.link_button(
                        "▶ Watch Trailer",
                        trailers[idx]
                    )

                else:
                    st.write("Trailer Not Available")

                # movie card end
                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )
            st.image(posters[4])
