import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt

# Load Netflix dataset
@st.cache_data
def load_data():
    df = pd.read_csv("netflix_titles.csv")
    df['date_added'] = pd.to_datetime(df['date_added'])
    return df

df = load_data()

# App title
st.title("Netflix Dashboard")

# Sidebar filters
st.sidebar.header("Filters")
selected_type = st.sidebar.selectbox("Select Type", ['All'] + df['type'].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Select Country", ['All'] + df['country'].dropna().unique().tolist())
selected_year = st.sidebar.slider("Select Release Year", int(df['release_year'].min()), int(df['release_year'].max()), (2000, 2020))

# Apply filters
filtered_df = df.copy()
if selected_type != 'All':
    filtered_df = filtered_df[filtered_df['type'] == selected_type]
if selected_country != 'All':
    filtered_df = filtered_df[filtered_df['country'] == selected_country]
filtered_df = filtered_df[(filtered_df['release_year'] >= selected_year[0]) & (filtered_df['release_year'] <= selected_year[1])]

# Show dataset
st.subheader("Filtered Data")
st.dataframe(filtered_df)

# Visualization 1: Content by Type
st.subheader("Content Distribution by Type")
type_counts = df['type'].value_counts()
st.bar_chart(type_counts)

# Visualization 2: Top 10 Countries with Most Titles
st.subheader("Top 10 Countries with Most Titles")
country_counts = df['country'].value_counts().nlargest(10)
st.bar_chart(country_counts)

# Visualization 3: Content Over Time
st.subheader("Content Added Over Time")
time_data = df.groupby(df['date_added'].dt.year).count()['show_id'].dropna()
st.line_chart(time_data)

# Choropleth Map for Netflix Content by Country
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="country names",
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(input_df[input_column].dropna())),
                               scope="world",
                               labels={input_column: 'Number of Titles'}
                              )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

# Heatmap Function
def make_heatmap(input_df, x_col, y_col, value_col, color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
        x=alt.X(x_col, title="Year"),
        y=alt.Y(y_col, title="Country"),
        color=alt.Color(value_col, scale=alt.Scale(scheme=color_theme), title="Number of Titles"),
        tooltip=[x_col, y_col, value_col]
    ).properties(width=600, height=400)
    return heatmap

# Donut Chart for Netflix Content by Release Year
def make_donut(input_response, input_text, input_color):
    chart_colors = {
        'blue': ['#29b5e8', '#155F7A'],
        'green': ['#27AE60', '#12783D'],
        'orange': ['#F39C12', '#875A12'],
        'red': ['#E74C3C', '#781F16']
    }
    chart_color = chart_colors.get(input_color, ['#29b5e8', '#155F7A'])
    
    source = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100 - input_response, input_response]
    })
    source_bg = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100, 0]
    })
    
    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value",
        color=alt.Color("Topic:N", scale=alt.Scale(domain=[input_text, ''], range=chart_color), legend=None)
    ).properties(width=130, height=130)
    
    text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="% value",
        color=alt.Color("Topic:N", scale=alt.Scale(domain=[input_text, ''], range=chart_color), legend=None)
    ).properties(width=130, height=130)
    
    return plot_bg + plot + text

# Display Total Titles by Country and Year
st.markdown('#### Total Titles')
choropleth = make_choropleth(df, 'country', 'show_id', 'plasma')
st.plotly_chart(choropleth, use_container_width=True)

heatmap_data = df.groupby(['release_year', 'country']).size().reset_index(name='title_count')
heatmap = make_heatmap(heatmap_data, 'release_year', 'country', 'title_count', 'plasma')
st.altair_chart(heatmap, use_container_width=True)

# Display Top Countries by Netflix Titles
st.markdown('#### Top Countries')
top_countries_df = df['country'].value_counts().reset_index()
top_countries_df.columns = ['Country', 'Title Count']
st.dataframe(top_countries_df, hide_index=True)

with st.expander('About', expanded=True):
    st.write('''
        - Data: Netflix dataset
        - :orange[**Most Content-Producing Countries**]: Top countries by number of Netflix titles
        - :orange[**Content Trends**]: Distribution of titles across different years
        ''')
