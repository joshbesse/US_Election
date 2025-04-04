import pandas as pd

# load US election data (by state)
df = pd.read_csv('./dataverse_files/1976-2020-president.csv')

# filter for winning candidate per state per year
idx = df.groupby(['year', 'state'])['candidatevotes'].idxmax()
state_winner = df.loc[idx, ['year', 'state', 'candidate', 'party_simplified', 'candidatevotes', 'totalvotes']]

# filter out DISTRICT OF COLUMBIA rows
state_winner = state_winner[state_winner['state'] != 'DISTRICT OF COLUMBIA']

# map party to party color
state_winner['color'] = state_winner['party_simplified'].map({'DEMOCRAT': 'blue', 'REPUBLICAN': 'red'})

# calculate percentage of votes that the winner received
state_winner['pctvotes'] = (state_winner['candidatevotes'] / state_winner['totalvotes'] * 100).round(1)

# save data
state_winner.to_csv('./election_data.csv')
print(state_winner.head(20))
print('Data has been saved.')