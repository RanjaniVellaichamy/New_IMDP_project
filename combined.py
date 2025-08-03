import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_option_menu import option_menu

st.set_page_config(page_title="🎥 Movie Dashboard", layout="wide")

# Sidebar selectbox
st.sidebar.title("Menu")
selected = st.sidebar.selectbox(
    "Choose a view:",
    [
        "Top Rated Movies", "Top Voted Movies", "Movie Count", "Average Duration", "Average Voting",
        "Top-Rated by Genre", "Vote Pie Chart", "Duration Extremes", "Rating Heatmap", "Rating vs Voting Scatter",
        "Interactive Filtering"
    ]
)

# Global variables
movie_data_path = "updatedfile.csv"
data_folder = "moviecsvfiles"

# Helper function

def find_column(df, candidates):
    for col in df.columns:
        if col.strip().lower() in candidates:
            return col
    return None

# 1. Top Rated Movies
if selected == "Top Rated Movies":
    st.title("🌟 Top Rated Movies")
    df = pd.read_csv(movie_data_path)
    top_rated = df.nlargest(10, 'movierating')
    st.write(top_rated)

# 2. Top Voted Movies
elif selected == "Top Voted Movies":
    st.title("🗳️ Top Voted Movies")
    df = pd.read_csv(movie_data_path)
    top_voted = df.nlargest(10, 'movievoting')
    st.write(top_voted)

# 3. Movie Count
elif selected == "Movie Count":
    st.title("🎬 Movie Count per Genre")
    csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
    movie_counts = {}
    for file in csv_files:
        try:
            df = pd.read_csv(os.path.join(data_folder, file))
            movie_counts[file] = len(df)
        except Exception as e:
            st.error(f"Error reading {file}: {e}")
    count_df = pd.DataFrame(movie_counts.items(), columns=["CSV File", "Movie Count"])
    fig, ax = plt.subplots()
    ax.bar(count_df["CSV File"], count_df["Movie Count"], color="skyblue")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

# 4. Average Duration
elif selected == "Average Duration":
    st.title("🕒 Average Duration per Genre")
    csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
    avg_duration = {}
    for file in csv_files:
        try:
            df = pd.read_csv(os.path.join(data_folder, file))
            col = find_column(df, ['durationtomins'])
            if col:
                avg = df[col].dropna().astype(float).mean()
                avg_duration[file] = round(avg, 2)
        except Exception as e:
            st.error(f"Error in {file}: {e}")
    df_dur = pd.DataFrame(avg_duration.items(), columns=["CSV File", "Average Duration"])
    fig, ax = plt.subplots()
    ax.barh(df_dur["CSV File"], df_dur["Average Duration"], color="mediumseagreen")
    st.pyplot(fig)

# 5. Average Voting
elif selected == "Average Voting":
    st.title("📊 Average Voting per Genre")
    csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
    avg_vote = {}
    for file in csv_files:
        try:
            df = pd.read_csv(os.path.join(data_folder, file))
            col = find_column(df, ['movievoting'])
            if col:
                avg = df[col].dropna().astype(int).mean()
                avg_vote[file] = round(avg, 2)
        except Exception as e:
            st.error(f"Error: {e}")
    df_vote = pd.DataFrame(avg_vote.items(), columns=["CSV File", "Average Voting"])
    fig, ax = plt.subplots()
    ax.bar(df_vote["CSV File"], df_vote["Average Voting"], color="coral")
    st.pyplot(fig)

# 6. Top-Rated by Genre
elif selected == "Top-Rated by Genre":
    st.title("🏆 Top-Rated Movie in Each Genre")
    csv_files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]
    selected_files = st.multiselect("Select CSV files:", csv_files)
    top_movies = []
    for file in selected_files:
        try:
            df = pd.read_csv(os.path.join(data_folder, file))
            title_col = find_column(df, ['moviename', 'movievoting', 'movieduration'])
            rating_col = find_column(df, ['movierating'])
            if title_col and rating_col:
                df[rating_col] = pd.to_numeric(df[rating_col], errors='coerce')
                df = df.dropna(subset=[rating_col])
                top = df.loc[df[rating_col].idxmax()]
                top_movies.append({"CSV File": file, "Title": top[title_col], "Rating": round(top[rating_col], 2)})
        except Exception as e:
            st.error(f"Error reading {file}: {e}")
    if top_movies:
        st.dataframe(pd.DataFrame(top_movies))

# 7. Vote Pie Chart
elif selected == "Vote Pie Chart":
    st.title("🥧 Top-Voted Movie Pie Chart")
    csv_files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]
    selected_files = st.multiselect("Select CSV files:", csv_files)
    top_votes = []
    for file in selected_files:
        try:
            df = pd.read_csv(os.path.join(data_folder, file))
            title_col = find_column(df, ['moviename'])
            vote_col = find_column(df, ['movievoting'])
            df[vote_col] = pd.to_numeric(df[vote_col], errors='coerce')
            df = df.dropna(subset=[vote_col])
            top = df.loc[df[vote_col].idxmax()]
            top_votes.append({"Label": f"{top[title_col]} ({file})", "Votes": int(top[vote_col])})
        except Exception as e:
            st.error(f"Error: {e}")
    if top_votes:
        df_votes = pd.DataFrame(top_votes)
        fig, ax = plt.subplots()
        ax.pie(df_votes["Votes"], labels=df_votes["Label"], autopct='%1.1f%%', startangle=140)
        st.pyplot(fig)

# 8. Duration Extremes
elif selected == "Duration Extremes":
    st.title("📏 Shortest and Longest Movies")
    csv_files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]
    selected_files = st.multiselect("Select CSV files:", csv_files)
    results = []
    for file in selected_files:
        try:
            df = pd.read_csv(os.path.join(data_folder, file))
            title_col = find_column(df, ['moviename'])
            duration_col = find_column(df, ['durationtomins'])
            df[duration_col] = pd.to_numeric(df[duration_col], errors='coerce')
            df = df.dropna(subset=[duration_col])
            shortest = df.loc[df[duration_col].idxmin()]
            longest = df.loc[df[duration_col].idxmax()]
            results.append({
                "CSV File": file,
                "Shortest Movie": shortest[title_col],
                "Shortest Duration": shortest[duration_col],
                "Longest Movie": longest[title_col],
                "Longest Duration": longest[duration_col]
            })
        except Exception as e:
            st.error(f"Error: {e}")
    if results:
        st.dataframe(pd.DataFrame(results))

# 9. Rating Heatmap
elif selected == "Rating Heatmap":
    st.title("🔥 Average Rating Heatmap")
    csv_files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]
    selected_files = st.multiselect("Select CSV files:", csv_files)
    ratings_data = []
    for file in selected_files:
        try:
            df = pd.read_csv(os.path.join(data_folder, file))
            rating_col = find_column(df, ['movierating'])
            df[rating_col] = pd.to_numeric(df[rating_col], errors='coerce')
            avg_rating = df[rating_col].dropna().mean()
            ratings_data.append({"CSV File": file, "Average Rating": round(avg_rating, 2)})
        except Exception as e:
            st.error(f"Error: {e}")
    if ratings_data:
        ratings_df = pd.DataFrame(ratings_data).set_index("CSV File")
        fig, ax = plt.subplots(figsize=(8, len(ratings_df)*0.6))
        sns.heatmap(ratings_df, annot=True, cmap="YlGnBu", linewidths=0.5)
        st.pyplot(fig)

# 10. Rating vs Voting Scatter
elif selected == "Rating vs Voting Scatter":
    st.title("📈 Ratings vs Voting Counts")
    csv_files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]
    selected_files = st.multiselect("Select CSV files:", csv_files)
    all_data = []
    for file in selected_files:
        try:
            df = pd.read_csv(os.path.join(data_folder, file))
            r_col = find_column(df, ['movierating'])
            v_col = find_column(df, ['movievoting'])
            df[r_col] = pd.to_numeric(df[r_col], errors='coerce')
            df[v_col] = pd.to_numeric(df[v_col], errors='coerce')
            df = df.dropna(subset=[r_col, v_col])
            df["CSV File"] = file
            df = df.rename(columns={r_col: "Rating", v_col: "Votes"})
            all_data.append(df)
        except Exception as e:
            st.error(f"Error: {e}")
    if all_data:
        combined = pd.concat(all_data)
        fig, ax = plt.subplots()
        for file in combined["CSV File"].unique():
            subset = combined[combined["CSV File"] == file]
            ax.scatter(subset["Votes"], subset["Rating"], label=file)
        ax.legend()
        ax.set_xlabel("Votes")
        ax.set_ylabel("Rating")
        ax.set_title("Ratings vs Votes")
        st.pyplot(fig)
def find_column(df, candidates):
    for col in df.columns:
        if col.strip().lower() in candidates:
            return col
    return None
# === 11. Interactive Filtering ===
if selected == "Interactive Filtering":
    st.title("🎬 Interactive Movie Filtering Across CSV Files")

    # === Setup ===
    csv_files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]
    #csv_files=pd.read_csv(movie_data_path)
    selected_files = st.multiselect("📁 Select CSV Files to Load", csv_files)

    title_candidates = ['moviename']
    duration_candidates = ['durationtomins']
    rating_candidates = ['movierating']
    vote_candidates = ['movievoting']
   # genre_candidates = ['genre']

    all_movies = []
    for file in selected_files:
        path = os.path.join(data_folder, file)
        try:
            df = pd.read_csv(path)
            title_col = find_column(df, title_candidates)
            duration_col = find_column(df, duration_candidates)
            rating_col = find_column(df, rating_candidates)
            vote_col = find_column(df, vote_candidates)
            #genre_col = find_column(df, genre_candidates)

            if not all([title_col, duration_col, rating_col, vote_col]):
                st.warning(f"⚠️ Skipping '{file}' (missing required columns)")
                continue

            df = df[[title_col, duration_col, rating_col, vote_col]]
            df.columns = ["Title", "Duration", "Rating", "Votes"]

            df["Duration"] = pd.to_numeric(df["Duration"], errors="coerce") / 60
            df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
            df["Votes"] = pd.to_numeric(df["Votes"], errors="coerce")
            df["Source File"] = file
            #df["Genre"] = df["Genre"].astype(str).str.split(",")
            #df = df.explode("Genre")
            #df["Genre"] = df["Genre"].str.strip()
            all_movies.append(df.dropna())

        except Exception as e:
            st.error(f"❌ Error loading {file}: {e}")

    if not all_movies:
        st.stop()

    combined_df = pd.concat(all_movies, ignore_index=True)

    # === Sidebar Filters ===
    st.sidebar.header("🔍 Filter Options")
    duration_filter = st.sidebar.radio("🎞️ Duration (Hours)", ["All", "< 2", "2–3", "> 3"])
    rating_filter = st.sidebar.slider("⭐ Minimum Rating", 0.0, 10.0, 0.0, 0.1)
    vote_filter = st.sidebar.number_input("🗳️ Minimum Votes", min_value=0, value=0, step=1000)
    #genre_list = sorted(combined_df["Genre"].dropna().unique())
    #genre_filter = st.sidebar.multiselect("🎭 Genres", genre_list)

    filtered_df = combined_df.copy()

    if duration_filter == "< 2":
        filtered_df = filtered_df[filtered_df["Duration"] < 2]
    elif duration_filter == "2–3":
        filtered_df = filtered_df[(filtered_df["Duration"] >= 2) & (filtered_df["Duration"] <= 3)]
    elif duration_filter == "> 3":
        filtered_df = filtered_df[filtered_df["Duration"] > 3]

    filtered_df = filtered_df[filtered_df["Rating"] >= rating_filter]
    filtered_df = filtered_df[filtered_df["Votes"] >= vote_filter]

    #if genre_filter:
        #filtered_df = filtered_df[filtered_df["Genre"].isin(genre_filter)]

    st.subheader(f"🎯 Filtered Results ({len(filtered_df)} Movies)")
    st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
