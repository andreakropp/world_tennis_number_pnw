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

    ratings['Date'] = pd.to_datetime(ratings['Date'], format='mixed')
    ratings['Rating'] = pd.to_numeric(ratings['Rating'], errors='coerce')

    # Exclude Low confidence ratings
    ratings = ratings[ratings['Confidence'] != 'Low']

    return ratings, profiles

ratings_df, profiles_df = load_data()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Player Ratings", "Statistics", "Player Profiles", "Doubles Comparison", "Singles Comparison"])

with tab1:
    st.header("Player Rating Trends")

    players = sorted(ratings_df['Name'].unique())
    selected_player = st.selectbox("Select a player:", players)

    player_data = ratings_df[ratings_df['Name'] == selected_player]

    # Calculate shared y-axis range for both charts
    singles_data = player_data[player_data['Format'] == 'Singles'].sort_values('Date')
    doubles_data = player_data[player_data['Format'] == 'Doubles'].sort_values('Date')

    # Find min and max across both formats
    all_ratings = []
    if not singles_data.empty:
        all_ratings.extend(singles_data['Rating'].tolist())
    if not doubles_data.empty:
        all_ratings.extend(doubles_data['Rating'].tolist())

    if all_ratings:
        y_min = min(all_ratings)
        y_max = max(all_ratings)

        # Ensure at least 2.0 range
        range_size = y_max - y_min
        if range_size < 2.0:
            padding = (2.0 - range_size) / 2
            y_min = y_min - padding
            y_max = y_max + padding
        else:
            # Add small padding for visual comfort
            padding = range_size * 0.05
            y_min = y_min - padding
            y_max = y_max + padding
    else:
        y_min, y_max = None, None

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Singles")
        if not singles_data.empty:
            # Select only the columns needed for plotting to avoid multiple series
            plot_data = singles_data[['Date', 'Rating']].copy()
            fig = px.line(plot_data, x='Date', y='Rating',
                         title=f'{selected_player} - Singles Rating',
                         markers=True)
            fig.update_layout(
                yaxis_title="WTN Rating",
                xaxis_title="Date",
                yaxis_range=[y_min, y_max]
            )
            st.plotly_chart(fig, use_container_width=True)
            st.metric("Current Singles Rating",
                     f"{singles_data.iloc[-1]['Rating']:.2f}",
                     f"Confidence: {singles_data.iloc[-1]['Confidence']}")
        else:
            st.info("No singles rating data available")

    with col2:
        st.subheader("Doubles")
        if not doubles_data.empty:
            # Select only the columns needed for plotting to avoid multiple series
            plot_data = doubles_data[['Date', 'Rating']].copy()
            fig = px.line(plot_data, x='Date', y='Rating',
                         title=f'{selected_player} - Doubles Rating',
                         markers=True)
            fig.update_layout(
                yaxis_title="WTN Rating",
                xaxis_title="Date",
                yaxis_range=[y_min, y_max]
            )
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
    top_players = latest_ratings.nsmallest(10, 'Rating')[['Name', 'Rating', 'Format', 'Confidence']]
    st.dataframe(top_players, hide_index=True, use_container_width=True)

with tab3:
    st.header("Player Profiles")

    merged_data = profiles_df.merge(
        ratings_df[ratings_df['Date'] == ratings_df['Date'].max()],
        on=['Name', 'UAID'],
        how='left'
    ).sort_values('Name')

    st.dataframe(
        merged_data[['Name', 'NTRP_2026', 'Rating', 'Format', 'Confidence', 'WTN_Profile']],
        hide_index=True,
        use_container_width=True,
        column_config={
            "WTN_Profile": st.column_config.LinkColumn("Profile Link")
        }
    )

with tab4:
    st.header("Doubles Comparison")

    # Filter for doubles data with at least 2 data points per player
    doubles_df = ratings_df[ratings_df['Format'] == 'Doubles'].copy()

    # Count data points per player
    player_counts = doubles_df.groupby('Name').size()
    players_with_multiple = player_counts[player_counts >= 2].index

    # Filter to only players with 2+ data points
    comparison_data = doubles_df[doubles_df['Name'].isin(players_with_multiple)].sort_values('Date')

    if not comparison_data.empty:
        fig = px.line(comparison_data, x='Date', y='Rating', color='Name',
                     title='Doubles Rating Comparison Over Time',
                     markers=True)
        fig.update_layout(
            height=2000,
            yaxis_title="WTN Doubles Rating",
            xaxis_title="Date",
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.01
            )
        )

        # Add text labels at the end of each line
        for player in players_with_multiple:
            player_data = comparison_data[comparison_data['Name'] == player]
            if not player_data.empty:
                last_point = player_data.iloc[-1]
                fig.add_annotation(
                    x=last_point['Date'],
                    y=last_point['Rating'],
                    text=player,
                    showarrow=False,
                    xanchor='left',
                    xshift=10,
                    font=dict(size=10)
                )

        st.plotly_chart(fig, use_container_width=True)
        st.info(f"Showing {len(players_with_multiple)} players with 2 or more doubles ratings")
    else:
        st.info("No players with multiple doubles ratings available")

with tab5:
    st.header("Singles Comparison")

    # Filter for singles data with at least 2 data points per player
    singles_df = ratings_df[ratings_df['Format'] == 'Singles'].copy()

    # Count data points per player
    player_counts = singles_df.groupby('Name').size()
    players_with_multiple = player_counts[player_counts >= 2].index

    # Filter to only players with 2+ data points
    comparison_data = singles_df[singles_df['Name'].isin(players_with_multiple)].sort_values('Date')

    if not comparison_data.empty:
        fig = px.line(comparison_data, x='Date', y='Rating', color='Name',
                     title='Singles Rating Comparison Over Time',
                     markers=True)
        fig.update_layout(
            height=2000,
            yaxis_title="WTN Singles Rating",
            xaxis_title="Date",
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.01
            )
        )

        # Add text labels at the end of each line
        for player in players_with_multiple:
            player_data = comparison_data[comparison_data['Name'] == player]
            if not player_data.empty:
                last_point = player_data.iloc[-1]
                fig.add_annotation(
                    x=last_point['Date'],
                    y=last_point['Rating'],
                    text=player,
                    showarrow=False,
                    xanchor='left',
                    xshift=10,
                    font=dict(size=10)
                )

        st.plotly_chart(fig, use_container_width=True)
        st.info(f"Showing {len(players_with_multiple)} players with 2 or more singles ratings")
    else:
        st.info("No players with multiple singles ratings available")

st.sidebar.markdown("---")
st.sidebar.info(f"Last updated: {ratings_df['Date'].max().strftime('%Y-%m-%d')}")
st.sidebar.info(f"Total players tracked: {len(ratings_df['Name'].unique())}")
