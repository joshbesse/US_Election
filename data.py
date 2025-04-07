import pandas as pd

def format_hover_text(row, candidates):
    c1, c2 = candidates[0], candidates[1]

    def get_color(party):
        if 'DEM' in party:
            return 'blue'
        else:
            return 'red'

    def line(name, pct, votes, party):
        color = get_color(party)
        name_html = f"{name:<20}".replace(" ", "&nbsp;")
        pct_html = f"{pct:>6.1f}%".rjust(10).replace(" ", "&nbsp;")
        vote_html = f"{int(votes):,}".rjust(12).replace(" ", "&nbsp;")

        return f"<span style='color:{color}'>{name_html}{pct_html}{vote_html}</span>"

    header = (
        "<b>" + row['state'] + "</b><br>" +
        "<span style='font-family:Courier'><b>" +
        f"{'Candidate':<20}".replace(" ", "&nbsp;") +
        f"{'%':>6}".rjust(10).replace(" ", "&nbsp;") +
        f"{'Votes':>12}".rjust(12).replace(" ", "&nbsp;") +
        "</b><br>"
    )

    line1 = line(c1, row[f'pctvotes_{c1}'], row[f'candidatevotes_{c1}'], row[f'party_{c1}'])
    line2 = line(c2, row[f'pctvotes_{c2}'], row[f'candidatevotes_{c2}'], row[f'party_{c2}'])

    return header + line1 + "<br>" + line2 + "</span>"

# load US election data (by state)
df = pd.read_csv('./dataverse_files/1976-2020-president.csv')

# drop unnecessary columns
df.drop(['state_fips', 'state_cen', 'state_ic', 'office', 'writein', 'version', 'notes', 'party_detailed'], axis=1, inplace=True)

# rename columns
df = df.rename(columns={'state_po': 'state_code', 'party_simplified': 'party'})

# filter for only democrat and republican candidates
df = df[(df['party'] == 'DEMOCRAT') | (df['party'] == 'REPUBLICAN')]
df = df[(df['candidate'] != 'OTHER') & (~df['candidate'].isna())]

# calculate percentage of votes candidate received'OTHER'
df['pctvotes'] = (df['candidatevotes'] / df['totalvotes'] * 100).round(1) 

# create pivot dataset for each year -> one row per state (increase app performance by limiting repeated data manipulation in app)
# loop through each year
for year in df['year'].unique():
    # filter data for specific year
    df_year = df[df['year'] == year]

    # pivot data -> one row per state with data on each candidate
    pivot = df_year.pivot_table(
        index=['state', 'state_code'],
        columns='candidate',
        values=['pctvotes', 'candidatevotes', 'party'],
        aggfunc='first'
    ).reset_index()

    # flatten multi-index columns
    pivot.columns = ['_'.join([part for part in col if part]).strip() if isinstance(col, tuple) else col for col in pivot.columns]

    # calculate winning candidate (based on percentage of votes received)
    candidates = df_year['candidate'].unique()
    pivot['winning_party'] = pivot.apply(lambda row: row[f'party_{candidates[0]}'] if row[f'pctvotes_{candidates[0]}'] > row[f'pctvotes_{candidates[1]}'] else row[f'party_{candidates[1]}'], axis=1)

    # create hover text for map (displayed when state is hovered on the map)
    pivot['hover_text'] = pivot.apply(lambda row: format_hover_text(row, candidates), axis=1)

    # save dataset for each year
    pivot.to_pickle(f'./data/{year}_election.pkl')
    print(f"Saved {year} election data.")

# load election results with electoral vote and popular vote
results = pd.read_excel('./data/Election_Results.xlsx')

# save as pickle file for performance (faster to read)
results.to_pickle('./data/results.pkl')
print("Saved results data.")
