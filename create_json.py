import pandas as pd
from calculate_segregation import calculate_scores
import json

data = pd.read_csv('clean_data.csv')
# Make column names lower case
data.columns = [d.lower() for d in data.columns]

# Fix name column
del data['name']
data = data.rename(columns={'name/address': 'name'})

districts = data.dist_id.unique()
with open('dist_lookup.json', 'r') as f:
    dist_ids = json.load(f)

scores = calculate_scores()
scores = scores.set_index('district')
scores = scores[['score', 'rank']].to_dict()

col_names = ['name', 'irish', 'non-irish', 'total']

# Remove trailing .0 from json
data[['irish', 'non-irish', 'total']].astype(int)

output = {}

for d in districts:
    district_schools = data[data.dist_id == d]
    school_data = district_schools[col_names].to_dict('records')
    score = scores['score'][d]
    rank = scores['rank'][d]

    district_name = dist_ids[d].replace(' [SS]', '')
    output[d] = {'schools': school_data,
               'score': score,
               'rank': rank,
               'name': district_name}

with open('schools_data.json', 'w') as f:
    json.dump(output, f)
