"""
Get a list of addresses for a specified postcode from a local copy of
FIAS database.
"""

import pandas as pd


def _query_postcode(pc: str, sql_engine) -> pd.DataFrame:
    """Query the database for all addresses belonging to this postcode
    and return them as a pandas DataFrame (as they are in the database).
    """
    query = f'''select * from fias where postalcode='{pc}';'''
    return pd.read_sql_query(query, sql_engine)


def _make_addresses(query: pd.DataFrame) -> pd.DataFrame:
    """Convert source FIAS DataFrame into a list of readable
    addresses (with GUIDs)."""
    qs = query.sort_values(by=[
        'region_f', 'area_f', 'city_f', 'quarter_f', 'place_f', 'terr_f',
        'street_f', 'housenum', 'buildnum', 'strucnum'
    ]).fillna('')
    addr = (qs.region_s + ' ' + qs.region_f + ', ' +
            qs.area_s + ' ' + qs.area_f + ', ' +
            qs.city_s + ' ' + qs.city_f + ', ' +
            qs.quarter_s + ' ' + qs.quarter_f + ', ' +
            qs.place_s + ' ' + qs.place_f + ', ' +
            qs.terr_s + ' ' + qs.terr_f + ', ' +
            qs.street_s + ' ' + qs.street_f + ', ' +
            qs.housenum + ', ' + qs.buildnum + ', ' + qs.strucnum)
    addr = addr.str.replace(r'[, ]{2,}', ', ', regex=True).str.strip()
    addr = addr.str.replace('"', '')
    addr = addr.str.strip(',')
    guids = qs.guid
    addr_df = pd.concat([guids, addr], axis=1, keys=['guid', 'addr'])
    return addr_df.reset_index(drop=True)


def get_address_list(pc: str, sql_engine) -> pd.Series:
    """Return a list of addresses for a given postcode."""
    pc_df = _query_postcode(pc, sql_engine)
    return _make_addresses(pc_df)