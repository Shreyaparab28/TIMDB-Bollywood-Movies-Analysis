import streamlit as st
import pandas as pd
import plotly.express as px

# Load datasets
@st.cache_data
def load_data():
    genre_timeline = pd.read_csv("genre_timeline.csv")
    ratings_by_decade = pd.read_csv("ratings_by_decade.csv")
    genre_blending = pd.read_csv("genre_blending.csv")
    bollywood_full_split = pd.read_csv("bollywood_full_preprocessed_split.csv")
    actor_director_collab = pd.read_csv("merged_actor_director_data.csv")
    return genre_timeline, ratings_by_decade, genre_blending, bollywood_full_split, actor_director_collab

# Load datasets
genre_timeline, ratings_by_decade, genre_blending, bollywood_full_split, actor_director_collab = load_data()

# Add calculated columns where needed
if 'decade' not in bollywood_full_split.columns:
    bollywood_full_split['decade'] = (bollywood_full_split['year_of_release'] // 10) * 10

# Ensure 'collaboration_count' exists in actor-director collaboration
if 'collaboration_count' not in actor_director_collab.columns:
    actor_director_collab['collaboration_count'] = actor_director_collab.groupby(['actor', 'name'])['imdb_id'].transform('count')

# Sidebar filters
st.sidebar.header("Filters")
selected_genre = st.sidebar.selectbox("Select Genre", options=[None] + list(genre_timeline['genre'].unique()))
selected_decade = st.sidebar.selectbox("Select Decade", options=[None] + list(ratings_by_decade['decade'].unique()))
selected_actor = st.sidebar.selectbox("Select Actor", options=[None] + list(actor_director_collab['actor'].unique()))
selected_director = st.sidebar.selectbox("Select Director", options=[None] + list(actor_director_collab['name'].unique()))

# Filtered datasets
filtered_data = bollywood_full_split.copy()
if selected_genre:
    filtered_data = filtered_data[
        (filtered_data['genre1'] == selected_genre) |
        (filtered_data['genre2'] == selected_genre) |
        (filtered_data['genre3'] == selected_genre)
    ]
if selected_decade:
    filtered_data = filtered_data[filtered_data['decade'] == selected_decade]
if selected_actor:
    if 'actors' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['actors'].str.contains(selected_actor, na=False)]
    else:
        st.error("The 'actors' column is missing in the dataset.")
if selected_director:
    if 'directors' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['directors'].str.contains(selected_director, na=False)]
    else:
        st.error("The 'directors' column is missing in the dataset.")

# Visualization 1: Genre Popularity Timeline
st.header("Genre Popularity Over Time")
filtered_timeline = genre_timeline.copy()
if selected_genre:
    filtered_timeline = filtered_timeline[filtered_timeline['genre'] == selected_genre]
fig_genre = px.scatter(
    filtered_timeline,
    x="year_of_release",
    y="count",
    size="count",
    color="genre",
    title="Genre Popularity Over Time",
    labels={"year_of_release": "Year", "count": "Number of Movies"},
    size_max=30
)
st.plotly_chart(fig_genre, use_container_width=True)

# Visualization 2: IMDb Ratings by Decade
st.header("IMDb Ratings by Decade")
filtered_ratings = ratings_by_decade.copy()
if selected_genre:
    genre_filtered_data = bollywood_full_split[
        (bollywood_full_split['genre1'] == selected_genre) |
        (bollywood_full_split['genre2'] == selected_genre) |
        (bollywood_full_split['genre3'] == selected_genre)
    ]
    filtered_ratings = genre_filtered_data.groupby('decade').agg(avg_imdb_rating=('imdb_rating', 'mean')).reset_index()
    filtered_ratings.rename(columns={'avg_imdb_rating': 'imdb_rating'}, inplace=True)
fig_ratings = px.bar(
    filtered_ratings,
    x="decade",
    y="imdb_rating",
    title=f"Average IMDb Ratings by Decade {'for ' + selected_genre if selected_genre else ''}",
    labels={"decade": "Decade", "imdb_rating": "Average IMDb Rating"},
    color="imdb_rating",
    color_continuous_scale="Blues"
)
st.plotly_chart(fig_ratings, use_container_width=True)

# Visualization 3: Genre Blending Trends
st.header("Genre Blending Trends")
filtered_genre_blending = genre_blending.copy()
if selected_genre:
    filtered_genre_blending = filtered_genre_blending[
        filtered_genre_blending['genre_combination'].str.contains(selected_genre, case=False)
    ]
fig_blending = px.bar(
    filtered_genre_blending.head(10),
    x="count",
    y="genre_combination",
    orientation="h",
    title="Top Genre Combinations",
    labels={"count": "Number of Movies", "genre_combination": "Genre Combination"},
    color="count",
    color_continuous_scale="sunset"
)
st.plotly_chart(fig_blending, use_container_width=True)

# Visualization 4: Actor-Director Collaboration Network
st.header("Actor-Director Collaboration Network")
filtered_collab = actor_director_collab.copy()
if selected_actor:
    filtered_collab = filtered_collab[filtered_collab['actor'] == selected_actor]
if selected_director:
    filtered_collab = filtered_collab[filtered_collab['name'] == selected_director]
fig_collab = px.scatter(
    filtered_collab,
    x="actor",
    y="name",
    size="collaboration_count",
    color="collaboration_count",
    title="Top Actor-Director Collaborations",
    labels={"actor": "Actor", "name": "Director", "collaboration_count": "Collaborations"},
    size_max=40
)
st.plotly_chart(fig_collab, use_container_width=True)

# Visualization 5: Winning Trends by Year
st.header("Winning Trends by Year")
wins_by_year = filtered_data.groupby(['year_of_release', 'genre1'])['wins'].sum().reset_index()
fig_wins_trends = px.line(
    wins_by_year,
    x='year_of_release',
    y='wins',
    color='genre1',
    title="Winning Trends Over the Years",
    labels={"year_of_release": "Year", "wins": "Number of Wins", "genre1": "Genre"},
    line_shape="spline",
    markers=True
)
st.plotly_chart(fig_wins_trends, use_container_width=True)
