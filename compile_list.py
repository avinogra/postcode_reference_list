"""
Create a reference postcode list based on the results of postcode
verification:
- fias verification cache
- hopeless postcodes verification cache
"""

import sys

import pandas as pd


FIAS_CACHE_FN = 'cache.csv'
HOPELESS_CACHE_FN = 'hopeless_cache.csv'
REFERENCE_LIST_FN = 'reference_list.csv'


def main() -> int:
    """Execute the list compilation script."""
    fias = pd.read_csv(FIAS_CACHE_FN, sep=';', dtype=str)
    hpls = pd.read_csv(HOPELESS_CACHE_FN, sep=';', dtype=str)
    hpls_confirmed = hpls.loc[hpls.status == 'confirmed']
    all_pcs = fias.pc.append(hpls_confirmed.target).drop_duplicates()
    all_pcs.sort_values(inplace=True)
    all_pcs.name = 'pc6'
    all_pcs.to_csv(REFERENCE_LIST_FN, sep=';', index=False)
    print(f'Reference list sucessfully saved as: {REFERENCE_LIST_FN}')


if __name__ == '__main__':
    sys.exit(main())
