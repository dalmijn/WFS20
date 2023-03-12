from wfs20 import __path__
from wfs20.io import GDAL_INSTALLED

import os
import sys
import sqlite3

if GDAL_INSTALLED:
	from osgeo import osr

# 0,5,6 are hard to define.
_OrienTable = {
	0:"xy",
	1:"yx",
	2:"yx",
	3:"xy",
	4:"xy",
	5:"xy",
	6:"xy"	
}

def execute_query(conn, query):
    cur = conn.cursor()
    try:
        cur.execute(query)
        conn.commit()
    except Exception as e:
        print(f"The error '{e}' occurred")
    cur.close()

def execute_read_query(conn, query):
    cur = conn.cursor()
    r = None
    try:
        cur.execute(query)
        r = cur.fetchall()
        return r
    except Exception as e:
        print(f"The error '{e}' occurred")
    cur.close()

def _CreateAxisOrderDBASE():
	"""
	"""
	# Some locations
	pyloc = os.path.dirname(sys.executable)
	# database connections
	proj = sqlite3.connect(f"{pyloc}\\Lib\\site-packages\\osgeo\\data\\proj\\proj.db")
	conn = sqlite3.connect(f"{__path__[0]}\\data\\axisorder.db")
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
	for crs_type in ["projected_crs","geodetic_crs","vertical_crs","compound_crs"]:
		for code in tuple(proj_cur.execute(f"SELECT code FROM {crs_type} WHERE auth_name = 'EPSG';")):
			srs = osr.SpatialReference()
			srs.ImportFromEPSG(code[0])
			url = f"http://epsg.io/{code[0]}"
			order = _OrienTable[srs.GetAxisOrientation(None,0)]
			print(srs.GetAxisOrientation(None,0))
			add_to_table = f"""\
INSERT INTO
  	axisorder ('auth','code','order','reference')
VALUES
  	("EPSG",{code[0]},'{order}','{url}')
"""
			execute_query(conn, add_to_table)
			print(f"Succesfully added EPSG:{code[0]}")
			# clean up the srs
			srs = None
	# close all connections and cursors
	conn.close()
	proj_cur.close()
	proj.close()

if __name__ == "__main__":
	_CreateAxisOrderDBASE()