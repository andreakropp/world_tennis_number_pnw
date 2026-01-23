import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="World Tennis Number - PNW", layout="wide")

st.title("World Tennis Number - Pacific Northwest Players")

@st.cache_data
def load_data():
    ratings = pd.read_csv('data/wtn_ratings.csv', encoding='utf-8-sig')
    profiles = pd.read_csv('data/wtn_profile_links.csv', encoding='utf-8-sig')

    ratings['Date'] = pd.to_datetime(ratings['Date'])
    ratings['Rating'] = pd.to_numeric(ratings['Rating'], errors='coerce')

    return ratings, profiles

ratings_df, profiles_df = load_data()

tab1, tab2, tab3 = st.tabs(["Player Ratings", "Statistics", "Player Profiles"])

with tab1:
    st.header("Player Rating Trends")

    players = sorted(ratings_df['Name'].unique())
    selected_player = st.selectbox("Select a player:", players)

    player_data = ratings_df[ratings_df['Name'] == selected_player]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Singles")
        singles_data = player_data[player_data['Format'] == 'Singles']
        if not singles_data.empty:
            fig = px.line(singles_data, x='Date', y='Rating',
                         title=f'{selected_player} - Singles Rating',
                         markers=True)
            fig.update_layout(yaxis_title="WTN Rating", xaxis_title="Date")
            st.plotly_chart(fig, use_container_width=True)
            st.metric("Current Singles Rating",
                     f"{singles_data.iloc[-1]['Rating']:.2f}",
                     f"Confidence: {singles_data.iloc[-1]['Confidence']}")
        else:
            st.info("No singles rating data available")

    with col2:
        st.subheader("Doubles")
        doubles_data = player_data[player_data['Format'] == 'Doubles']
        if not doubles_data.empty:
            fig = px.line(doubles_data, x='Date', y='Rating',
                         title=f'{selected_player} - Doubles Rating',
                         markers=True)
            fig.update_layout(yaxis_title="WTN Rating", xaxis_title="Date")
            st.plotly_chart(fig, use_container_width=True)
            st.metric("Current Doubles Rating",
                     f"{doubles_data.iloc[-1]['Rating']:.2f}",
                     f"Confidence: {doubles_data.iloc[-1]['Confidence']}")
        else:
            st.info("No doubles rating data available")

with tab2:
    st.header("Rating Statistics")

    format_choice = st.radio("Select format:", ['Singles', 'Doubles', 'Both'])

    if format_choice == 'Both':
        filtered_data = ratings_df
    else:
        filtered_data = ratings_df[ratings_df['Format'] == format_choice]

    latest_date = filtered_data['Date'].max()
    latest_ratings = filtered_data[filtered_data['Date'] == latest_date]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Players", len(latest_ratings['Name'].unique()))
    with col2:
        st.metric("Average Rating", f"{latest_ratings['Rating'].mean():.2f}")
    with col3:
        st.metric("Rating Range",
                 f"{latest_ratings['Rating'].min():.2f} - {latest_ratings['Rating'].max():.2f}")

    st.subheader("Rating Distribution")
    fig = px.histogram(latest_ratings, x='Rating', nbins=20,
                      title=f'Rating Distribution ({format_choice})')
    fig.update_layout(xaxis_title="WTN Rating", yaxis_title="Number of Players")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 Players by Rating")
    top_players = latest_ratings.nlargest(10, 'Rating')[['Name', 'Rating', 'Format', 'Confidence']]
    st.dataframe(top_players, hide_index=True, use_container_width=True)

with tab3:
    st.header("Player Profiles")

    merged_data = profiles_df.merge(
        ratings_df[ratings_df['Date'] == ratings_df['Date'].max()],
        on=['Name', 'UAID'],
        how='left'
    )

    st.dataframe(
        merged_data[['Name', 'NTRP_2026', 'Rating', 'Format', 'Confidence', 'WTN_Profile']],
        hide_index=True,
        use_container_width=True,
        column_config={
            "WTN_Profile": st.column_config.LinkColumn("Profile Link")
        }
    )

st.sidebar.markdown("---")
st.sidebar.info(f"Last updated: {ratings_df['Date'].max().strftime('%Y-%m-%d')}")
st.sidebar.info(f"Total players tracked: {len(ratings_df['Name'].unique())}")
