"""Create the axisorder database."""

import os
import sqlite3
import sys
from pathlib import Path

from pyproj.crs import CRS

# 0,5,6 are hard to define.
_OrienTable_old = {0: "xy", 1: "yx", 2: "yx", 3: "xy", 4: "xy", 5: "xy", 6: "xy"}
_OrienTable = {"west": "xy", "east": "xy", "north": "yx", "south": "yx"}


def execute_query(conn, query):
    """Execute a query."""
    cur = conn.cursor()
    try:
        cur.execute(query)
        conn.commit()
    except Exception as e:
        sys.stdout.write(f"The error '{e}' occurred\n")
    cur.close()


def create_database():
    """Create the axisorder database via the proj.db used by GDAL."""
    # Some locations
    db_dir = os.environ.get("PROJ_DATA", os.environ.get("PROJ_LIB"))
    if db_dir is None:
        raise ConnectionError("Proj database was not found.")

    # database connections
    proj = sqlite3.connect(Path(db_dir, "proj.db"))
    conn = sqlite3.connect(Path(pwd, "src", "wfs20", "data", "axisorder.db"))
    # set cursor
    proj_cur = proj.cursor()
    create_table = """\
CREATE TABLE IF NOT EXISTS axisorder (
'auth' TEXT NOT NULL,
'code' INTEGER PRIMARY KEY AUTOINCREMENT,
'order' TEXT NOT NULL,
'reference' TEXT
);
"""
    execute_query(conn, create_table)
    for crs_type in ["projected_crs", "geodetic_crs", "vertical_crs", "compound_crs"]:
        for code in tuple(
            proj_cur.execute(f"SELECT code FROM {crs_type} WHERE auth_name = 'EPSG';")
        ):
            srs = CRS.from_epsg(code[0])
            url = f"http://epsg.io/{code[0]}"
            direction = srs.axis_info[0].direction
            sys.stdout.write(f"Direction is: {direction}\n")
            order = _OrienTable[direction]
            add_to_table = f"""\
INSERT INTO
      axisorder ('auth','code','order','reference')
VALUES
      ("EPSG",{code[0]},'{order}','{url}')
"""
            execute_query(conn, add_to_table)
            sys.stdout.write(f"Succesfully added EPSG:{code[0]}\n")
            # clean up the srs
            srs = None
    # close all connections and cursors
    conn.close()
    proj_cur.close()
    proj.close()


if __name__ == "__main__":
    pwd = Path(__file__).parent
    create_database()
