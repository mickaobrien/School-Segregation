import fiona
import json

SHP_FILE = './garda-sub-districts/Census2011_Garda_SubDistricts_Nov2013/Census2011_Garda_Subdistricts_Nov2013.shp'

def create_lookup():
    """
    Create JSON file containing dict mapping district ID to name.
    """
    with fiona.open(SHP_FILE) as fc:
        lookup = {f['properties']['SUB_CODE']: f['properties']['SUB_DIST'] for f in fc}

    with open('dist_lookup.json', 'w') as f:
        json.dump(lookup, f)


if __name__=='__main__':
    create_lookup()
