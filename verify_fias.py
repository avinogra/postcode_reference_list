"""
Check FIAS vs. pochta.ru

Verify every postcode in FIAS if it exists on pochta.ru.
"""

import sys

import pandas as pd
import sqlalchemy

from library.fias_sql_connection import CONNECTION
from library.fias_summary_sql import generate_summary
from library.address_from_sql import get_address_list
from library.index_by_address import get_postcode

LOCAL_CACHE = 'cache.csv'


def load_cache(filename: str) -> pd.DataFrame:
    """Load local address/pc cache or create one if it doesn't exist."""
    try:
        cache = pd.read_csv(LOCAL_CACHE, sep=';', dtype=str)
    except FileNotFoundError:
        print(f'Cache at {LOCAL_CACHE} not found. Starting from scratch.')
        cache = pd.DataFrame(columns=['guid', 'address', 'pc'])
    return cache


def save_cache(cache: pd.DataFrame, filename: str) -> None:
    """Save cache to a file."""
    cache.to_csv(filename, sep=';', index=False)
    print(f'\nCache saved as {filename}')


def cleanup(cache: pd.DataFrame, sql_engine) -> None:
    """Wrap up script's open resources."""
    sql_engine.dispose()
    cache = cache.loc[cache.pc != 'error']
    save_cache(cache, LOCAL_CACHE)


def exists_in_cache(postcode: str, cache: pd.DataFrame) -> bool:
    """Return True if the `postcode` exists in cache."""
    match = cache.loc[cache.pc == postcode]
    return False if match.empty else True


def remove_cached(batch: pd.DataFrame, cache: pd.DataFrame) -> pd.DataFrame:
    """Remove cached addresses from the batch."""
    unchecked = batch.loc[~batch.guid.isin(cache.guid)]
    return unchecked


def check_batch(batch: pd.DataFrame, target_pc: str) -> pd.DataFrame:
    """Check a batch of addresses online.

    Return a DataFrame with results.
    If target postcode is within the results - return as soon as target
    postcode is found.
    """
    data = pd.DataFrame()
    for guid, address in batch.itertuples(index=False):
        print(f'--- {guid[:8]}… {address[-50:]:<51}: ', end='', flush=True)
        return_pc = get_postcode(address)
        print(return_pc)
        data_dict = {'target': target_pc, 'guid': guid,
                     'address': address, 'pc': return_pc}
        data_row = pd.DataFrame(data_dict, index=[0])
        data = data.append(data_row, ignore_index=True)
        if target_pc == return_pc:
            print('--- ✓ Match!')
            break
    return data


def main() -> int:
    """Run the script."""
    print('Loading resources… ', end='', flush=True)
    cache = load_cache(LOCAL_CACHE)
    pgsql = sqlalchemy.create_engine(CONNECTION)
    fiass = generate_summary(pgsql)
    print('done.')

    print('Downloading PCs:')
    for postcode in fiass.postalcode:
        print(f'- {postcode}')
        if exists_in_cache(postcode, cache):
            continue
        batch = get_address_list(postcode, pgsql)
        batch = remove_cached(batch, cache)
        batch = batch.sample(frac=1).iloc[:500]
        try:
            results = check_batch(batch, postcode)
            cache = cache.append(results, ignore_index=True)
        except KeyboardInterrupt:
            print('\nTerminated by user.')
            cleanup(cache, pgsql)
            return 1

    cleanup(cache, pgsql)
    return 0


if __name__ == '__main__':
    sys.exit(main())
