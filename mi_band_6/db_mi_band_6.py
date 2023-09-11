"""
Based on the gadget bridge database of the MI Band 6.
"""

import sqlite3

class MiBandDb:

    def __init__(self, db_file:str):
        self.db_file                    = db_file
        self._conn                      = None

        self._open_db()

    def _open_db(self):
        self._conn = sqlite3.connect(self.db_file)

    def __del__(self):
        if self._conn:
            self._conn.close()

    def get_raw
