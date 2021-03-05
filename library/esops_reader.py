"""
A function to read the ESOPS dataset.
"""

import geopandas as gpd
import pandas as pd


def read_esops(filename: str) -> pd.DataFrame:
    """Read the ESOPS dataset, strip excessive columns and return as a
    pandas DataFrame.
    """
    KEEP_COLUMNS = ['INDEX', 'OPSNAME', 'OPSTYPE']
    esops = gpd.read_file(filename)
    esops = esops[KEEP_COLUMNS]
    return esops
