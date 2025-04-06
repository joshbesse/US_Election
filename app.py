import streamlit as st
import pandas as pd
import plotly.graph_objects as go

@st.cache_data
def load_data_for_year(year):
    return pd.read_pickle(f'./data/{year}_election.pkl')

# radio button for year selection
selected_year = st.sidebar.radio('Select Year', range(1976, 2021, 4))

# load data for chosen year
df_year = load_data_for_year(selected_year)

# create election map for chosen year
fig = go.Figure(data=go.Choropleth(
    locations=df_year['state_code'],
    z=df_year['winning_party'].map({'DEMOCRAT': 0, 'REPUBLICAN': 1}),
    locationmode='USA-states',
    colorscale=[[0, 'blue'], [1, 'red']],
    showscale=False,
    text=df_year['hover_text'],
    hovertemplate="%{text}<extra></extra>"
))

fig.update_layout(
    geo_scope='usa',
    margin=dict(l=0, r=0, t=0, b=0)
)

st.plotly_chart(fig, use_container_width=True)

