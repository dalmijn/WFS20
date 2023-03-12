from wfs20.crs import CRS
from wfs20.error import WFSInternalError
from wfs20.io import _WriteGeometries
from wfs20.reader import _ServiceReader, DataReader
from wfs20.request import _ServiceURL, CreateGetRequest
from wfs20.util import _BuildServiceMeta

import sys

class WebFeatureService:
	def __init__(
		self,
		url: str,
		version: str="2.0.0"
	) -> 'WebFeatureService':
		"""WebFeatureService

		Parameters
		----------

		url : str
			Service url
		version : str
			WebFeatureService version
		
		Returns
		-------
		wfs20.WebFeatureService
			Object containing the metadata of the service
		"""

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
		featuretype: str,
		bbox: tuple,
		epsg: int,
		):
		"""Request spatial data from the WebFeatureService

		Parameters
		----------
		featuretype : str
			Layer to be requested, mostly in the format of 'xxx:xxx'
		bbox : tuple
			Bounding box wherein the spatial data lies that is requested,
			e.g. (x1,y1,x2,y2)
		epsg : int
			The projection code of the requested data and the bounding box 
			according to EPSG, e.g. 4326 (WGS84)

		Returns
		-------
		wfs20.reader.DataReader
			Contains the requested data
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
		keyword = self.FeatureTypeMeta[featuretype].Title
		self.DataReader = DataReader(url,keyword)
		return self.DataReader

	def ToFile(
		self,
		out: str,
		driver: str="GeoJSON",
		):
		"""Write geospatial data held in reader to file

		Parameters
		----------
		out : str
			path of where the file should be written to
		driver : str
			ogr driver for writing the geometries
			E.g. 'GeoJSON' if one wants to write the data
			in the geojson format
		"""
		
		if self.DataReader == None or not self.DataReader.Features:
			raise WFSInternalError("Writing to file","No features collected from WebFeatureService")
		_WriteGeometries(self.DataReader,driver,out)
		