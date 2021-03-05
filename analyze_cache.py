"""
Analyze FIAS checking cache

Classify all postcodes in FIAS into three categories:
1. confirmed
2. exhausted
3. unconfirmed
based on the contents of the local address/postcode cache file.
"""

import sys

import pandas as pd
import sqlalchemy

from library.fias_sql_connection import CONNECTION
from library.fias_summary_sql import generate_summary


LOCAL_CACHE = 'cache.csv'
SUMMARY_FILENAME = 'summary.csv'


def load_cache(filename: str) -> pd.DataFrame:
    """Load local cache from file and return as a DataFrame."""
    cache = pd.read_csv(LOCAL_CACHE, sep=';', dtype=str)
    return cache


def load_fias_summary(conn: str) -> pd.DataFrame:
    """Connect to a local FIAS database and generate a summary. Return
    as a DataFrame.
    """
    pgsql = sqlalchemy.create_engine(conn)
    fiass = generate_summary(pgsql)
    pgsql.dispose()
    return fiass


def exists_in_cache(postcode: str, cache: pd.DataFrame) -> bool:
    """Return True if the `postcode` exists in cache."""
    match = cache.loc[cache.pc == postcode]
    return False if match.empty else True


def remove_cached(batch: pd.DataFrame, cache: pd.DataFrame) -> pd.DataFrame:
    """Remove cached addresses from the batch."""
    unchecked = batch.loc[~batch.guid.isin(cache.guid)]
    return unchecked


def save_summary(summary: pd.DataFrame, filename: str) -> None:
    """Save summary to a file."""
    summary.to_csv(filename, sep=';', index=False)
    confirmed = summary.loc[summary.status == 'confirmed']
    exhausted = summary.loc[summary.status == 'exhausted']
    unconfirmed = summary.loc[summary.status == 'unconfirmed']
    print(f'Total postcodes in FIAS: {len(summary)}')
    print(f'- of them confirmed: {len(confirmed)}')
    print(f'- of them exhausted: {len(exhausted)}')
    print(f'- of them still unconfirmed: {len(unconfirmed)}')
    print(f'\nSummary saved as {filename}')


# ==================

def main() -> int:
    """Run the analysis script."""
    cache = load_cache(LOCAL_CACHE)
    fiass = load_fias_summary(CONNECTION)
    fiass['status'] = 'unconfirmed'
    cache_counts = cache.groupby('target').count().guid.reset_index()
    fiasm = pd.merge(fiass, cache_counts, how='left',
                     left_on=['postalcode', 'cnt'],
                     right_on=['target', 'guid'])
    fiasm.loc[fiasm.cnt == fiasm.guid, 'status'] = 'exhausted'
    fiasm.loc[fiasm.postalcode.isin(cache.pc), 'status'] = 'confirmed'
    save_summary(fiasm, SUMMARY_FILENAME)
    return 0


if __name__ == '__main__':
    sys.exit(main())
