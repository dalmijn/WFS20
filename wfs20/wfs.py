from wfs20.crs import CRS
from wfs20.error import WFSInternalError
from wfs20.io import _WriteShapeFile, _WriteToGML
from wfs20.reader import _ServiceReader, DataReader
from wfs20.request import _ServiceURL, CreateGetRequest
from wfs20.util import _BuildServiceMeta

import sys

class WebFeatureService:
	"""
	WebFeatureService

	Parameters
	----------

	url: str
		Service url
	version: str
		WebFeatureService version
	"""
	def __init__(self,url,version="2.0.0"):
		self.url = url
		self.version = version
		self.ServiceURL = _ServiceURL(self.url,version)

		# Substance
		_BuildServiceMeta(self, _ServiceReader(self.ServiceURL,timeout=30))

		# Declarations
		self.DataReader = None

	def __repr__(self):
		return f"<wfs20.WebFeatureService object ({self.url})>"

	def RequestData(
		self,
		featuretype,
		bbox,
		epsg
		):
		"""
		"""
		if featuretype not in self.FeatureTypes:
			raise WFSInternalError(
				"Request Error", 
				f"<{featuretype}> not in list of available featuretypes (see <class>.FeatureTypes)"
				)
		crs = CRS.from_epsg(epsg)
		if not crs in self.FeatureTypeMeta[featuretype].CRS:
			raise WFSInternalError(
				"Request Error", 
				f"<{epsg}> not in list of available projections (see <class>.FeatureTypeMeta[<id>].CRS)"
				)
		url = CreateGetRequest(
				self.url,
				self.version,
				featuretype,
				bbox,
				crs
				)
		self.DataReader = DataReader(url)
		return self.DataReader

	def ToFile(
		self,
		out,
		format="shp"
		):
		"""
		"""
		if self.DataReader == None or not self.DataReader.Features:
			raise WFSInternalError("Writing to file","No features collected from WebFeatureService")
		if format == "shp":
			_WriteShapeFile(self.DataReader,out)
		elif format == "gml":
			_WriteToGML()
		else:
			raise ValueError(f"Incorrect format => {format}")

if __name__ == "__main__":
	wfs = WebFeatureService(r"https://service.pdok.nl/lv/bag/wfs/v2_0?request=getCapabilities&service=WFS")
	print(wfs)
	# print(wfs.typenames)
	# print(wfs.Contraints)
	wfs.RequestData("bag:pand", (110000,451000,111000,452000), 28992)
	print(wfs.DataReader.LayerMeta.LinkTable)