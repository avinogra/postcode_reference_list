"""
A utility to generate FIAS summary from a SQL database.
"""

import pandas as pd
from sqlalchemy import create_engine


def generate_summary(sql_engine) -> pd.DataFrame:
    """Generate a FIAS summary DataFrame from a local copy of FIAS.

    It is assumed that FIAS is stored in a predefined `fias` table, with
    a predefined schema (same as standard Kantynent/ADDR delivery, sans
    the redundant `_en` and some other fields).

    `sql_engine` - SQLAlchemy engine.
    """
    query = '''
        SELECT postalcode, COUNT(*) AS cnt
        FROM fias
        WHERE postalcode IS NOT NULL
        GROUP BY postalcode;
        '''
    summary = pd.read_sql_query(query, sql_engine)
    return summary
