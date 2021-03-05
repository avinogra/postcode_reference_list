# Postcode reference list

Toolset that generates the reference postcode list.


## Requirements

1.  An up-to-date FIAS version is required for the tool to work.  
    It should be loaded to an SQL database. Connection credentials are
    saved in [library/sql_connection.py](library/sql_connection.py)

2.  An up-to-date ESOPS database (.dbf) is required to. ESOPS filename
    is configured in [verify_hopeless.py](verify_hopeless.py)


## Usage

1.  First run [verify_fias.py](verify_fias.py) to build a 'cache' of
    verification postcode responses from pochta.ru. The script supports
    interrupting so you can Ctrl-C any time and it will resume
    gracefully next time it is run.

2.  Once all postcodes in FIAS have been verified we can run
    [analyze_cache.py](analyze_cache.py) to assess the results of
    verification.

3.  Once all FIAS postcodes have been verified we must verify those that
    are in ESOPS and not in FIAS + all FIAS postcodes that have not been
    confirmed. It is done by running
    [verify_hopeless.py](verify_hopeless.py). This script supports
    interrupting (Ctrl-C) too. The result of running the script is a new
    cache file.

4.  One both caches (FIAS and hopeless) have been completed we can build
    the reference list itself. It is done by running [compile_list.py](compile_list.py).
    This creates `reference_list.csv`, which is the final artifact of
    this toolset.


## Edits

This version is the first working draft and can be edited as necessary
during later updates.
