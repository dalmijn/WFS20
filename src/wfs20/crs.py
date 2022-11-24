from wfs20 import __path__
from wfs20.error import WFSError
from wfs20.io.util import execute_read_query

import sqlite3

def _OrderFromDB(code):
	"""
	Get the order out of the database by EPSG code
	"""
	conn = sqlite3.connect(f"{__path__[0]}\\data\\axisorder.db")
	search_query = f"""\
SELECT * FROM axisorder WHERE code = '{code}';
"""
	r = execute_read_query(conn, search_query)
	conn.close()
	return r[0]

class CRS:
	"""
	CRS object

	Parameters
	----------
	crs: str
		crs in urn format or uri format
	
	Returns
	-------
	CRS object
	"""
	def __init__(self,crs):
		self.crs = crs
		self.na = "ogc"
		if "urn:" in self.crs:
			self.encoding = "urn"
			s = self.crs.split(":")
			self.na = s[1]
			self.auth = s[-3]
			self.version = s[-2]
			self.code = s[-1]
		elif "/def/crs/" in self.crs:
			self.encoding = "uri"
			s = self.crs.split("/")
			self.auth = s[-3].upper()
			self.version = s[-2]
			self.code = s[-1]
		elif "#" in self.crs:
			self.encoding = "uri"
			s = self.crs.split("/")
			self.auth = s[-1].split(".")[0].upper()
			self.code = s[-1].split("#")[-1]

		self.order = _OrderFromDB(self.code)[2]

	def __repr__(self):
		return f"<wfs20.crs.CRS object ({self.auth}:{self.code})>"

	def __eq__(self, other):
		if isinstance(self,other.__class__):
			return self.GetURNCode() == other.GetURNCode()
		else:
			return False

	@classmethod
	def from_epsg(cls,code,version=None):
		"""
		CRS object

		Parameters
		----------
		code: str
			Projection code according to EPSG
		"""
		if not version:
			version = ""
		crs_string = f"urn:ogc:def:crs:EPSG:{version}:{code}"
		return cls(crs_string)

	def GetURNCode(self):
		if self.version == 0:
			self.version = ""
		return f"urn:{self.na}:def:crs:{self.auth}:{self.version}:{self.code}"

	def GetURICode1(self):
		if not self.version:
			self.version = 0
		return f"http://www.opengis.net/def/crs/{self.auth}/{self.version}/{self.code}"