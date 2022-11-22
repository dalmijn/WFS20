from wfs20.error import WFSError
from wfs20.request import GetResponse

import json
import warnings

try:
	from osgeo.osr import SpatialReference
except ModuleNotFoundError:
	warnings.warn("osgeo package not installed. Creating CRS class will be slower",ImportWarning)

def _OrderFromOSR(code):
	srs = SpatialReference()
	srs.ImportFromEPSG(int(code))
	if srs.GetAxisOrientation(None,0) == 3:
		order = "xy"
	else:
		order = "yx"
	srs = None
	return order

def _OrderFromURL(code):
	url = f"http://epsg.io/{code}.json"
	try:
		r = GetResponse(url, timeout=30)
		status_code = None
	except WFSError as e:
		r = None
		status_code = e.code
	finally:
		if r:
			crs_json =  json.loads(r.text)
			axis = crs_json["coordinate_system"]["axis"]
			if any(["east" in item.lower() for item in axis[0].values()]):
				order = "xy"
			else:
				order = "yx"
		else:
			order = "xy"
	crs_json = None
	axis = None
	if status_code == 404:
		raise WFSError("CRS not found", status_code, f"code: {code}")
	return order

def _axisorder(code):
	try:
		order = _OrderFromOSR(code)
	except ModuleNotFoundError:
		order = _OrderFromURL(code)
	return order

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

		self.order = _axisorder(self.code)

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