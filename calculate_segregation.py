from math import log
import pandas as pd


def calculate_scores(data=None, district_type='dist_id'):
    """
    Calculate mutual information segregation scores,
    grouping schools by district_type.

    Returns pandas.DataFrame with score data.
    """
    if data is None:
        data = pd.read_csv('clean_data.csv')

    # Get list of different districts
    districts = data[district_type].unique()

    scores = []

    for d in districts:
        schools = data[data[district_type] == d]
        prop_non_irish = float(schools['Non-Irish'].sum())/schools['TOTAL'].sum()
        segregation_score = score(schools)
        school_data = (d, segregation_score, len(schools), prop_non_irish)
        scores.append(school_data)

    df = pd.DataFrame(scores)
    df.columns = ['district', 'score', 'number_schools', 'prop_non_irish']

    df = df.sort('score', ascending=False).reset_index()

    # Add rank and percentile columns
    df['rank'] = df['score'].rank(ascending=False)
    df['percentile'] = 100*(1 - df['score'].rank(ascending=False, pct=True))

    # Remove index column created by re-indexing
    del df['index']

    return df


def write_scores(scores, filename='scores.json'):
    scores.to_json(filename, orient='records')


def get_categories():
    return ['IRISH', 'Non-Irish']


def score(schools):
    """
    Calculate mutual information segregation score
    as defined in http://www2.econ.iastate.edu/faculty/frankel/segindex.pdf

    Score = h(P) - sum_over_n(pi_n, h(p_n))
    where h(x) is the Shannon entropy measure of x
    P is a vector of proportions of groups in each school
    pi_n is the proportion of students in school n
    p_n is a vector of the proportion of groups in school n

    """
    categories = get_categories()
    pn = schools[categories].apply(lambda x: x/schools['TOTAL'])

    h_pn = pn.applymap(entropy_val).sum(axis=1)

    pi_n = schools['TOTAL']/(schools['TOTAL'].sum())

    p = schools[categories].sum()/schools['TOTAL'].sum()
    h_p = p.apply(entropy_val).sum()

    segregation_score = h_p - (pi_n*h_pn).sum()

    return segregation_score


def entropy_val(x):
    if x == 0:
        return 0
    return x*log(1./x, 2)


def index_dissimilarity(schools):
    """
    Calculate the dissimilarity index for a region's schools.

    See: https://en.wikipedia.org/wiki/Index_of_dissimilarity
    """
    g1, g2 = get_categories()

    g1_total = schools[g1].sum()
    g2_total = schools[g2].sum()

    score = 0.5*abs(schools[g1]/g1_total - schools[g2]/g2_total).sum()

    return score


def gini_index(schools):
    """
    Calculates the Gini index as a measure of segregation in schools.
    """

    pi_n = (schools['TOTAL']/(schools['TOTAL'].sum())).tolist()

    g1, g2 = get_categories()
    p_g1 = schools[g1]/schools['TOTAL']
    P_g1 = schools[g1].sum()/schools['TOTAL'].sum()
    r_g1 = (p_g1/P_g1).tolist()

    p_g2 = schools[g2]/schools['TOTAL']
    P_g2 = schools[g2].sum()/schools['TOTAL'].sum()
    r_g2 = (p_g2/P_g2).tolist()

    score = 0
    for i in range(len(pi_n)):
        for j in range(len(pi_n)):
            score += P_g1*pi_n[i]*pi_n[j]*abs(r_g1[i] - r_g1[j]) \
                + P_g2*pi_n[i]*pi_n[j]*abs(r_g2[i] - r_g2[j])

    return score
