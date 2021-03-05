"""
Hopeless postcodes

Verify ESOPS postcodes that are not part of the FIAS and
FIAS postcodes that could not be verified while checking FIAS.
"""


import pandas as pd
import sys

from library.esops_reader import read_esops
from library.index_by_address import get_postcode
from library.po_metadata import get_PO_address


ESOPS_FN = 'data/PIndx03.dbf'
FIAS_CACHE_FN = 'cache.csv'
HOPELESS_CACHE_FN = 'hopeless_cache.csv'


def make_a_list_to_verify(esops_fn: str, fias_cache_fn: str) -> pd.Series:
    """Make a list of postcodes to be checked."""
    esops = read_esops(esops_fn)
    cache = pd.read_csv(fias_cache_fn, sep=';', dtype=str)
    all_fias_pcs = pd.Series(cache.target.unique())
    esops_unconfirmed = esops.INDEX.loc[~esops.INDEX.isin(cache.pc)]
    fias_unconfirmed = all_fias_pcs.loc[~all_fias_pcs.isin(cache.pc)]
    all_unconfirmed = esops_unconfirmed.append(fias_unconfirmed)
    all_unconfirmed = all_unconfirmed.drop_duplicates().reset_index(drop=True)
    return all_unconfirmed


def load_hopeless_cache(hopeless_cache_fn) -> pd.DataFrame:
    """Load 'hopeless' postcodes cache from a file or create a new one
    if it doesn't exist.
    """
    try:
        hopeless_cache = pd.read_csv(hopeless_cache_fn, sep=';', dtype=str)
    except FileNotFoundError:
        hopeless_cache = pd.DataFrame(columns=['target', 'address',
                                               'response', 'status'])
    return hopeless_cache


def remove_processed(full_list: pd.Series, cache: pd.DataFrame) -> pd.Series:
    """Remove postcodes that have already been verified (i.e. exist in
    cache) from the postcode list.
    """
    return full_list.loc[~full_list.isin(cache.target)].reset_index(drop=True)


def verify_postcode(postcode: str) -> dict:
    """Verify a postcode on pochta.ru and return a dictionary of status
    variables:

    `target`: source postcode that is being verified,
    `address`: an address of the post office designated by target PC,
    `response`: postcode that is returned by pochta.ru when searching
                for the `po_address`
    `status`: inclusion status of the postcode - either a `confirmed` or
              `declined`.
    """
    po_address = get_PO_address(postcode)
    if (po_address == 'error') or (po_address == 'no such P.O.'):
        po_postcode = 'n/a'
    else:
        po_postcode = get_postcode(po_address)
    status = 'confirmed' if po_postcode == postcode else 'declined'
    cache_row = {'target': postcode, 'address': po_address,
                 'response': po_postcode, 'status': status}
    return cache_row


def save_cache(cache: pd.DataFrame, filename: str) -> None:
    """Save a cache DataFrame to a file."""
    cache.to_csv(filename, sep=';', index=False)
    print(f'Cache successully saved to: {filename}')


def main() -> int:
    """Execute the verification script."""
    print('Loading hopeless postcode list: ', end='', flush=True)
    hopeless_pcs = make_a_list_to_verify(ESOPS_FN, FIAS_CACHE_FN)
    print('done.')
    print('Loading cache: ', end='', flush=True)
    hopeless_cache = load_hopeless_cache(HOPELESS_CACHE_FN)
    unverified = remove_processed(hopeless_pcs, hopeless_cache)
    print('done.')
    for postcode in unverified:
        print(f'{postcode}: ', end='', flush=True)
        try:
            cache_row = verify_postcode(postcode)
            hopeless_cache = hopeless_cache.append(cache_row,
                                                   ignore_index=True)
        except KeyboardInterrupt:
            print('\nTerminated by user...')
            break
        print(cache_row['status'])
    save_cache(hopeless_cache, HOPELESS_CACHE_FN)
    return 0


if __name__ == '__main__':
    sys.exit(main())
