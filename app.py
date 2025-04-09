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

def render_map(df_year, height=450, key=None):
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
        margin=dict(l=0, r=0, t=0, b=0),
        height=height
    )

    st.plotly_chart(fig, use_container_width=True, key=key)

def render_breakdown(df_year, df_result):
    def render_list(title, df, col):
        html = f"""
        <div style='padding: 1em; border-radius: 10px; font-family: sans-serif; background: #f9f9f9;'>
            <div style='font-weight: bold; font-size: 1.1em; margin-bottom: 0.5em;'>{title}</div>
            <div style='font-weight: bold; display: flex; justify-content: space-between; padding: 0.3em 0; border-bottom: 1px solid #ccc;'>
                <div style='flex: 2;'>State</div>
                <div style='flex: 1; text-align: right;'>%</div>
            </div>
        """

        for _, row in df.iterrows():
            html += f"""
            <div style='display: flex; justify-content: space-between; padding: 0.2em 0; font-size: 15px'>
                <div style='flex: 2;'>{row['state']}</div>
                <div style='flex: 1; text-align: right;'>{round(row[col], 1)}%</div>
            </div>
            """

        html += "</div>"
        components.html(html, height=210)

    most_dem = df_year.sort_values(f"pctvotes_{df_result.iloc[0]['dem_candidate']}", ascending=False).head(5)
    most_rep = df_year.sort_values(f"pctvotes_{df_result.iloc[0]['rep_candidate']}", ascending=False).head(5)
    most_contest = df_year.sort_values('abs_margin').head(5)

    render_list("🟦 Most Democratic States", most_dem, f"pctvotes_{df_result.iloc[0]['dem_candidate']}")
    render_list("🟥 Most Republican States", most_rep, f"pctvotes_{df_result.iloc[0]['rep_candidate']}")
    render_list("⚖️ Most Contested States", most_contest, 'abs_margin')

def render_comparison_breakdown(df_year1, df_result1, df_year2, df_result2):
    def render_results(df_result1, df_result2):
        # election results (year, winner, electoral votes)
        results_html = f"""
        <div style='padding: 1em; border-radius: 10px; font-family: sans-serif; background: #f9f9f9;'>
            <div style='font-weight: bold; font-size: 1.1em; margin-bottom: 0.5em;'>Election Results</div>
            <div style='font-weight: bold; display: flex; justify-content: space-between; padding: 0.3em 0; border-bottom: 1px solid #ccc;'>
                <div style='flex: 2;'>Year</div>
                <div style='flex: 4;'>Winning Candidate</div>
                <div style='flex: 4; text-align: center;'>Electoral Votes</div>
            </div>
        """

        row1, row2 = df_result1.iloc[0], df_result2.iloc[0]

        years = [row1['year'], row2['year']]
        candidates = [row1['win_candidate'], row2['win_candidate']]
        colors = [row1['win_party_color'], row2['win_party_color']]
        ele_votes = [row1['win_ele_votes'], row2['win_ele_votes']]
        ele_vote_pcts = [row1['win_ele_votes_pct'], row2['win_ele_votes_pct']]

        for i in range(2):
            results_html += f"""
            <div style='display: flex; justify-content: space-between; padding: 0.2em 0; font-size: 15px'>
                <div style='flex: 2;'>{years[i]}</div>
                <div style='flex: 4; text-align: left; color: {colors[i]}'>{candidates[i]}</div>
                <div style='flex: 4; text-align: center;'>{ele_votes[i]} ({ele_vote_pcts[i]}%)</div>
            </div>
            """

        components.html(results_html)

    def render_flipped(df_year1, df_year2):
        # flipped states
        flipped_html = f"""
        <div style='padding: 1em; border-radius: 10px; font-family: sans-serif; background: #f9f9f9;'>
            <div style='font-weight: bold; font-size: 1.1em; margin-bottom: 0.5em;'>States That Flipped</div>
            <div style='font-weight: bold; display: flex; justify-content: space-between; padding: 0.3em 0; border-bottom: 1px solid #ccc;'>
                <div style='flex: 2;'>State</div>
                <div style='flex: 2; text-align: center;'>From</div>
                <div style='flex: 2; text-align: center;'>To</div>
            </div>
        """

        flipped = pd.merge(df_year1, df_year2, on=['state', 'state_code'], suffixes=('_1', '_2'))
        flipped = flipped[flipped['winning_party_1'] != flipped['winning_party_2']][['state', 'winning_party_1', 'winning_party_2']]

        states = flipped['state'].values
        party1 = flipped['winning_party_1'].values
        party2 = flipped['winning_party_2'].values

        for i in range(len(states)):
            flipped_html += f"""
            <div style='display: flex; justify-content: space-between; padding: 0.2em 0; font-size: 15px'>
                <div style='flex: 2;'>{states[i]}</div>
                <div style='flex: 2; text-align: center;'>{party1[i]}</div>
                <div style='flex: 2; text-align: center;'>{party2[i]}</div>
            </div>
            """
        height = len(states) * 24 + 100
        components.html(flipped_html, height=height)

    def render_swings(df_year1, df_year2):
        # biggest swings in % votes
        swing_html = f"""
        <div style='padding: 1em; border-radius: 10px; font-family: sans-serif; background: #f9f9f9;'>
            <div style='font-weight: bold; font-size: 1.1em; margin-bottom: 0.5em;'>Biggest Swings in % Votes</div>
            <div style='font-weight: bold; display: flex; justify-content: space-between; padding: 0.3em 0; border-bottom: 1px solid #ccc;'>
                <div style='flex: 2;'>State</div>
                <div style='flex: 2; text-align: center;'>Swing</div>
                <div style='flex: 2; text-align: center;'>Toward</div>
            </div>
        """

        swing = pd.merge(df_year1, df_year2, on=['state', 'state_code'], suffixes=('_1', '_2'))
        swing['swing'] = swing['margin_2'] - swing['margin_1']
        swing['toward'] = swing['swing'].apply(lambda x: 'DEMOCRAT' if x > 0 else 'REPUBLICAN')
        swing['swing'] = swing['swing'].abs().round(1)

        biggest_swings = swing.sort_values('swing', ascending=False).head(5)
        states = biggest_swings['state'].values
        swings = biggest_swings['swing'].values
        towards = biggest_swings['toward'].values

        for i in range(5):
            swing_html += f"""
            <div style='display: flex; justify-content: space-between; padding: 0.2em 0; font-size: 15px'>
                <div style='flex: 2;'>{states[i]}</div>
                <div style='flex: 2; text-align: center;'>{swings[i]}%</div>
                <div style='flex: 2; text-align: center;'>{towards[i]}</div>
            </div>
            """

        components.html(swing_html, height=220)

    render_results(df_result1, df_result2)
    render_flipped(df_year1, df_year2)
    render_swings(df_year1, df_year2)

# set wide page layout
st.set_page_config(layout='wide')

# toggle button for toggling between standard page and map comparison page
toggle = st.toggle("Election Map Comparison")

# toggle between standard single map page and two map comparison page
if toggle:
    # set page layout (3 columns)
    c1, c2, c3 = st.columns([1, 4.2, 2.8])

    # COLUMN 1 - election years selection
    # radio buttons for years selection
    years = list(range(1976, 2025, 4))[::-1]
    selected_year1 = c1.radio('Select Election Year 1', years, index=1, horizontal=True, key='radio1')
    c1.markdown("<div style='margin-top: 120px;'></div>", unsafe_allow_html=True)
    selected_year2 = c1.radio('Select Election Year 2', years, index=0, horizontal=True, key='radio2')

    # COLUMN 2 - election maps
    # load data for chosen years
    df_year1, df_result1 = load_data_for_year(selected_year1)
    df_year2, df_result2 = load_data_for_year(selected_year2)

    with c2:
        st.markdown(f"<h3 style='margin-bottom: -1em;'>{selected_year1} Election</h3>", unsafe_allow_html=True)
        render_map(df_year1, 250, 'map1')
        st.markdown(f"<h3 style='margin-bottom: -1em;'>{selected_year2} Election</h3>", unsafe_allow_html=True)
        render_map(df_year2, 250, 'map2')
    
    # COLUMN 3 - comparison breakdown
    with c3:
        render_comparison_breakdown(df_year1, df_result1, df_year2, df_result2)

else:
    # set page layout (3 columns)
    c1, c2, c3 = st.columns([1, 5, 2])

    # COLUMN 1 - election year selection
    # radio button for year selection
    selected_year = c1.radio('Select Election Year', list(range(1976, 2025, 4))[::-1], index=0)

    # COLUMN 2 - election map
    # load data for chosen year
    df_year, df_result = load_data_for_year(selected_year)

    with c2:
        st.markdown(f"<h2 style='margin-bottom: -1em;'>{selected_year} Election</h2>", unsafe_allow_html=True)
        render_outcome(df_result)
        render_map(df_year)

    # COLUMN 3 - state breakdown
    with c3:
        render_breakdown(df_year, df_result)
