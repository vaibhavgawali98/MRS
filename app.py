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
    page_title="FlixVerse",
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
    background: linear-gradient(to bottom, #000000, #141414, #1f1f1f);
    color: white;
}

/* remove top spacing */
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
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(10px);
    padding: 12px;
    border-radius: 15px;
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

@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):

    try:

        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'

        response = requests.get(url)

        data = response.json()

        # if poster exists
        if data.get('poster_path'):

            poster_path = data['poster_path']

            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path

            return full_path

        else:
            return "https://via.placeholder.com/500x750?text=No+Image"

    except:
        return "https://via.placeholder.com/500x750?text=Error"

# =========================
# FETCH MOVIE TRAILER
# =========================

@st.cache_data(show_spinner=False)
def fetch_trailer(movie_id):

    try:

        url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"

        response = requests.get(url)

        data = response.json()

        # find trailer
        if data.get('results'):

            for video in data['results']:

                if (
                    video.get('type') == 'Trailer'
                    and video.get('site') == 'YouTube'
                ):

                    trailer_url = f"https://www.youtube.com/watch?v={video['key']}"

                    return trailer_url

        return None

    except:
        return None

# =========================
# FETCH MOVIE DETAILS
# =========================

@st.cache_data(show_spinner=False)
def fetch_movie_details(movie_id):

    try:

        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"

        response = requests.get(url)

        data = response.json()

        genres = []

        if data.get('genres'):

            genres = [g['name'] for g in data['genres']]

        return {

            "rating": data.get('vote_average', 'N/A'),

            "release_date": data.get('release_date', 'N/A'),

            "overview": data.get('overview', 'No overview available'),

            "genres": genres
        }

    except:

        return {

            "rating": "N/A",

            "release_date": "N/A",

            "overview": "No overview available",

            "genres": []
        }

# =========================
# RECOMMENDATION FUNCTION
# =========================

def recommend(movie):

    movie_list = movies[movies['title'] == movie]

    if movie_list.empty:
        st.error("Movie not found")
        return [], [], [], []

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
    movie_details = []

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

        # append details
        movie_details.append(
            fetch_movie_details(movie_id)
        )

    return movie_names, movie_posters, movie_trailers, movie_details

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

    st.markdown("---")

    st.write(f"🎬 Total Movies: {len(movies)}")

# =========================
# HERO SECTION
# =========================

st.markdown(
    "<div class='main-title'>🎬  ReelVerse AI</div>",
    unsafe_allow_html=True
)

# banner image
st.image(
    "https://wallpapercave.com/wp/wp8871710.jpg",
    use_container_width=True
)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# TRENDING MOVIES SECTION
# =========================

st.subheader("🔥 Trending Movies")

trending_movies = movies.sample(5)

trend_cols = st.columns(5)

for idx, col in enumerate(trend_cols):

    with col:

        movie_id = trending_movies.iloc[idx].movie_id

        st.image(
            fetch_poster(movie_id)
        )

        st.caption(
            trending_movies.iloc[idx].title
        )

# =========================
# MOVIE SEARCH
# =========================

selected_movie_name = st.selectbox(
    '🔍 Search your favorite movie',
    sorted(movies['title'].values),
    index=None,
    placeholder="Type movie name..."
)

# =========================
# RECOMMEND BUTTON
# =========================

if st.button('🎥 Recommend Movies'):

    if selected_movie_name is not None:

        # loading animation
        with st.spinner("Finding best movies for you..."):

            names, posters, trailers, details = recommend(selected_movie_name)

        # display recommendations
        if len(names) >= 5:

            st.subheader("🎬 Recommended Movies")

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

                    # match percentage
                    st.write(f"🔥 {90 - idx}% Match")

                    # progress bar
                    st.progress((90 - idx) / 100)

                    # movie rating
                    st.write(
                        f"⭐ Rating: {details[idx]['rating']}"
                    )

                    # genres
                    st.write(
                        "🎭 " + ", ".join(details[idx]['genres'][:2])
                    )

                    # release date
                    st.write(
                        f"📅 {details[idx]['release_date']}"
                    )

                    # trailer button
                    if trailers[idx]:

                        st.link_button(
                            "▶ Watch Trailer",
                            trailers[idx]
                        )

                    else:
                        st.write("Trailer Not Available")

                    # movie overview
                    with st.expander("Movie Overview"):

                        st.write(
                            details[idx]['overview']
                        )

                    # movie card end
                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True
                    )

    else:
        st.warning("Please select a movie first")

# =========================
# FOOTER
# =========================

st.markdown("---")

st.markdown(
    """
    <center>
    Made with ❤️ using Streamlit, TMDB API & Machine Learning
    </center>
    """,
    unsafe_allow_html=True
)
