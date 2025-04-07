import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

@st.cache_data
def load_data_for_year(year):
    df_year = pd.read_pickle(f'./data/{year}_election.pkl')
    df_results = pd.read_pickle('./data/results.pkl')
    df_results = df_results[df_results['year'] == int(f'{year}')]

    return df_year, df_results

def render_outcome(df_result):
    row = df_result.iloc[0]

    html = f"""
    <div style='padding: 1em; border-radius: 10px; font-family: sans-serif; margin-bottom: 0;'>
        <div style='font-weight: bold; display: flex; justify-content: space-between; padding: 0.3em 0; border-bottom: 1px solid #ccc;'>
            <div style='flex: 1;'>Candidate</div>
            <div style='flex: 1;'>Electoral Vote</div>
            <div style='flex: 1;'>Popular Vote</div>
        </div>

        <div style='display: flex; justify-content: space-between; padding: 0.4em 0; color: {row['win_party_color']}; font-weight: 600;'>
            <div style='flex: 1;'>✅ {row['win_candidate']}</div>
            <div style='flex: 1;'>{row['win_ele_votes']} ({row['win_ele_votes_pct']}%)</div>
            <div style='flex: 1;'>{row['win_pop_votes']:,} ({row['win_pop_votes_pct']}%)</div>
        </div>

        <div style='display: flex; justify-content: space-between; padding: 0.1em 0; color: {row['lose_party_color']};'>
            <div style='flex: 1;'>{row['lose_candidate']}</div>
            <div style='flex: 1;'>{row['lose_ele_votes']} ({row['lose_ele_votes_pct']}%)</div>
            <div style='flex: 1;'>{row['lose_pop_votes']:,} ({row['lose_pop_votes_pct']}%)</div>
        </div>
    </div>
    """

    components.html(html, height=110)

# create page layout (3 columns)
st.set_page_config(layout='wide')
c1, c2, c3 = st.columns([1, 5, 2])

# COLUMN 1 - election year selection
# radio button for year selection
selected_year = c1.radio('Select Year', range(1976, 2021, 4))

# COLUMN 2 - election map
# load data for chosen year
df_year, df_result = load_data_for_year(selected_year)

with c2:
    st.markdown(f"<h2 style='margin-bottom: -1em;'>1976 Election</h3>", unsafe_allow_html=True)
    render_outcome(df_result)

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